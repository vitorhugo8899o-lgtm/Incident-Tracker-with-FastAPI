from fastapi import APIRouter

router_monitoring = APIRouter()


@router_monitoring.get('/health')
async def check_status():
    return {'status': 'ok', 'version': '1.0.0'}
