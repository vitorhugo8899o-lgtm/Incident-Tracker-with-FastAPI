from fastapi import APIRouter, HTTPException
from sqlalchemy import text

from app.api.v1.dependencies import DBSession

router_monitoring = APIRouter()


@router_monitoring.get('/health')
async def check_status(db: DBSession):
    try:
        await db.execute(text('SELECT 1'))
        db_status = 'online'
    except Exception as e:  # pragma: no cover
        db_status = 'offline'
        raise HTTPException(
            status_code=503,
            detail={
                'status': 'error',
                'database': db_status,
                'error_msg': str(e),
            },
        )

    return {'status': 'ok', 'database': db_status, 'version': '1.0.0'}
