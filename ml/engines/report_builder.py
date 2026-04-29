from models.grooming_model.predict_grooming import predict_grooming

def build_report(messages):
 txt=' '.join(messages)
 risk=int(predict_grooming(txt)*100)
 return {
 'risk_score':risk,
 'recommendation':'alert_parent' if risk>70 else 'monitor'
 }
