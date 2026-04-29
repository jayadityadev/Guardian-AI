"""
WebSocket alerts: Real-time notification when analysis completes.
"""

from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status


router = APIRouter(tags=["alerts"])


class ConnectionManager:
	"""Manage WebSocket connections and broadcast alerts."""
	
	def __init__(self):
		self.active_connections: list[WebSocket] = []
	
	async def connect(self, websocket: WebSocket):
		await websocket.accept()
		self.active_connections.append(websocket)
	
	def disconnect(self, websocket: WebSocket):
		self.active_connections.remove(websocket)
	
	async def broadcast(self, message: dict):
		"""Broadcast alert to all connected clients."""
		for connection in self.active_connections:
			try:
				await connection.send_json(message)
			except Exception:
				# Client disconnected, will be handled by disconnect()
				pass


manager = ConnectionManager()


@router.websocket("/ws/alerts")
async def websocket_alerts(websocket: WebSocket):
	"""
	WebSocket endpoint for real-time analysis alerts.
	
	Clients connect here and receive alerts when new session analysis completes.
	Broadcasts: event, session_id, risk_score, recommendation
	"""
	await manager.connect(websocket)
	try:
		while True:
			# Keep connection alive, wait for messages from client (ping/pong)
			data = await websocket.receive_text()
			# Optionally echo back or ignore heartbeats
	except WebSocketDisconnect:
		manager.disconnect(websocket)


async def broadcast_analysis_complete(
	session_id: UUID,
	risk_score: int,
	recommendation: str,
):
	"""
	Call this after session analysis is complete to notify all connected clients.
	
	Args:
		session_id: UUID of the completed session
		risk_score: Risk score (0-100)
		recommendation: Recommendation (monitor, alert_parent, escalate_platform)
	"""
	message = {
		"event": "analysis_complete",
		"session_id": str(session_id),
		"risk_score": risk_score,
		"recommendation": recommendation,
	}
	await manager.broadcast(message)
