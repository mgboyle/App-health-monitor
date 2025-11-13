"""
Web routes for the health monitor application
"""
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash
from app.models import db, Endpoint, HealthCheck
from app.health_checker import HealthChecker
from datetime import datetime, timedelta
from sqlalchemy import func

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    """Home page showing all endpoints and their status"""
    endpoints = Endpoint.query.order_by(Endpoint.created_at.desc()).all()
    
    # Get latest status for each endpoint
    endpoint_statuses = []
    for endpoint in endpoints:
        latest_check = HealthChecker.get_latest_status(endpoint.id)
        endpoint_statuses.append({
            'endpoint': endpoint,
            'latest_check': latest_check
        })
    
    return render_template('index.html', endpoint_statuses=endpoint_statuses)


@bp.route('/endpoints/add', methods=['GET', 'POST'])
def add_endpoint():
    """Add a new endpoint"""
    if request.method == 'POST':
        name = request.form.get('name')
        url = request.form.get('url')
        endpoint_type = request.form.get('endpoint_type', 'REST')
        check_interval = int(request.form.get('check_interval', 60))
        timeout = int(request.form.get('timeout', 30))
        enabled = request.form.get('enabled') == 'on'
        
        if not name or not url:
            flash('Name and URL are required', 'error')
            return render_template('add_endpoint.html')
        
        endpoint = Endpoint(
            name=name,
            url=url,
            endpoint_type=endpoint_type,
            check_interval=check_interval,
            timeout=timeout,
            enabled=enabled
        )
        
        db.session.add(endpoint)
        db.session.commit()
        
        flash(f'Endpoint "{name}" added successfully', 'success')
        return redirect(url_for('main.index'))
    
    return render_template('add_endpoint.html')


@bp.route('/endpoints/<int:endpoint_id>/edit', methods=['GET', 'POST'])
def edit_endpoint(endpoint_id):
    """Edit an existing endpoint"""
    endpoint = Endpoint.query.get_or_404(endpoint_id)
    
    if request.method == 'POST':
        endpoint.name = request.form.get('name')
        endpoint.url = request.form.get('url')
        endpoint.endpoint_type = request.form.get('endpoint_type', 'REST')
        endpoint.check_interval = int(request.form.get('check_interval', 60))
        endpoint.timeout = int(request.form.get('timeout', 30))
        endpoint.enabled = request.form.get('enabled') == 'on'
        endpoint.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        flash(f'Endpoint "{endpoint.name}" updated successfully', 'success')
        return redirect(url_for('main.index'))
    
    return render_template('edit_endpoint.html', endpoint=endpoint)


@bp.route('/endpoints/<int:endpoint_id>/delete', methods=['POST'])
def delete_endpoint(endpoint_id):
    """Delete an endpoint"""
    endpoint = Endpoint.query.get_or_404(endpoint_id)
    name = endpoint.name
    
    db.session.delete(endpoint)
    db.session.commit()
    
    flash(f'Endpoint "{name}" deleted successfully', 'success')
    return redirect(url_for('main.index'))


@bp.route('/endpoints/<int:endpoint_id>/check', methods=['POST'])
def check_endpoint_now(endpoint_id):
    """Manually trigger a health check for an endpoint"""
    endpoint = Endpoint.query.get_or_404(endpoint_id)
    
    health_check = HealthChecker.check_endpoint(endpoint)
    db.session.add(health_check)
    db.session.commit()
    
    flash(f'Health check completed for "{endpoint.name}"', 'success')
    return redirect(url_for('main.index'))


@bp.route('/endpoints/<int:endpoint_id>/logs')
def endpoint_logs(endpoint_id):
    """View logs for a specific endpoint"""
    endpoint = Endpoint.query.get_or_404(endpoint_id)
    page = request.args.get('page', 1, type=int)
    per_page = 50
    
    # Get paginated health checks
    pagination = HealthCheck.query.filter_by(
        endpoint_id=endpoint_id
    ).order_by(
        HealthCheck.checked_at.desc()
    ).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    # Calculate statistics
    total_checks = HealthCheck.query.filter_by(endpoint_id=endpoint_id).count()
    success_checks = HealthCheck.query.filter_by(
        endpoint_id=endpoint_id,
        status='success'
    ).count()
    
    uptime_percentage = (success_checks / total_checks * 100) if total_checks > 0 else 0
    
    # Get average response time
    avg_response_time = db.session.query(
        func.avg(HealthCheck.response_time)
    ).filter(
        HealthCheck.endpoint_id == endpoint_id,
        HealthCheck.status == 'success'
    ).scalar() or 0
    
    stats = {
        'total_checks': total_checks,
        'success_checks': success_checks,
        'uptime_percentage': round(uptime_percentage, 2),
        'avg_response_time': round(avg_response_time, 2)
    }
    
    return render_template(
        'logs.html',
        endpoint=endpoint,
        pagination=pagination,
        stats=stats
    )


@bp.route('/logs')
def all_logs():
    """View all logs across all endpoints"""
    page = request.args.get('page', 1, type=int)
    per_page = 50
    
    # Get paginated health checks with endpoint information
    pagination = db.session.query(
        HealthCheck, Endpoint
    ).join(
        Endpoint
    ).order_by(
        HealthCheck.checked_at.desc()
    ).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    return render_template('all_logs.html', pagination=pagination)


@bp.route('/api/health')
def health_api():
    """API endpoint returning health status of all endpoints"""
    endpoints = Endpoint.query.filter_by(enabled=True).all()
    
    results = []
    overall_healthy = True
    
    for endpoint in endpoints:
        latest_check = HealthChecker.get_latest_status(endpoint.id)
        
        endpoint_status = {
            'name': endpoint.name,
            'url': endpoint.url,
            'type': endpoint.endpoint_type,
            'status': 'unknown',
            'last_checked': None
        }
        
        if latest_check:
            endpoint_status['status'] = latest_check.status
            endpoint_status['status_code'] = latest_check.status_code
            endpoint_status['response_time_ms'] = latest_check.response_time
            endpoint_status['last_checked'] = latest_check.checked_at.isoformat()
            endpoint_status['error_message'] = latest_check.error_message
            
            if latest_check.status != 'success':
                overall_healthy = False
        else:
            overall_healthy = False
        
        results.append(endpoint_status)
    
    return jsonify({
        'status': 'healthy' if overall_healthy else 'unhealthy',
        'timestamp': datetime.utcnow().isoformat(),
        'endpoints': results
    })


@bp.route('/api/endpoints')
def api_endpoints():
    """API endpoint returning all endpoints"""
    endpoints = Endpoint.query.all()
    return jsonify({
        'endpoints': [endpoint.to_dict() for endpoint in endpoints]
    })


@bp.route('/api/endpoints/<int:endpoint_id>/checks')
def api_endpoint_checks(endpoint_id):
    """API endpoint returning health checks for a specific endpoint"""
    endpoint = Endpoint.query.get_or_404(endpoint_id)
    limit = request.args.get('limit', 100, type=int)
    
    checks = HealthCheck.query.filter_by(
        endpoint_id=endpoint_id
    ).order_by(
        HealthCheck.checked_at.desc()
    ).limit(limit).all()
    
    return jsonify({
        'endpoint': endpoint.to_dict(),
        'checks': [check.to_dict() for check in checks]
    })
