import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
from ml.models.url_model.predict_url import predict_url
cases = [
    'https://amazon.com',
    'login to verify account',
    'secure your password',
    'claim your free refund',
    'meet me tomorrow alone',
    'update your bank session',
    'http://account-unusual-activity.cf',
    'http://45.88.120.3/verify'
]
for c in cases:
    r = predict_url(c)
    print(c, '->', r['is_grooming'], r['risk_score'], r['matched_keywords'], r['detection_method'])
