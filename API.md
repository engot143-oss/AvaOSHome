# AVA OS API Reference

Dashboard and export API endpoints.

## Stats & Monitoring

### GET `/api/stats`
Get conversation and notification counts.

**Response:**
```json
{
  "conversation_turns": 42,
  "notifications": 5,
  "topics_discussed": {"nursing": 10, "finance": 8},
  "topics_learned": 2
}
```

### GET `/api/safety`
Get security statistics and rate limit status.

**Response:**
```json
{
  "total_violations": 0,
  "by_type": {},
  "rate_limit_remaining": 95,
  "conversation_turns_remaining": 98
}
```

## Conversation History

### GET `/api/conversations`
List conversation history with optional filtering.

**Parameters:**
- `topic` (optional) — Filter by topic (nursing, finance, life_skills, medical)
- `limit` (optional) — Max results (default: 50)

**Response:**
```json
[
  {
    "timestamp": "2026-08-19T10:30:00",
    "role": "user",
    "text": "What do nurses do?",
    "topic": "nursing"
  }
]
```

## Notifications

### GET `/api/notifications`
Get parent notification alerts.

**Parameters:**
- `limit` (optional) — Max results (default: 50)

**Response:**
```json
[
  {
    "timestamp": "2026-08-19T10:35:00",
    "topic": "NURSING",
    "message": "Discussed nursing career path"
  }
]
```

## Knowledge Base

### GET `/api/knowledge`
Get facts for a specific age and topic.

**Parameters:**
- `age` (optional) — Age (default: 10)
- `topic` (optional) — Topic (nursing, finance, life_skills)

**Response:**
```json
[
  {
    "id": "nursing-01",
    "title": "What nurses actually do every day",
    "explanation": "...",
    "complexity": "BEGINNER",
    "topic": "nursing",
    "verified": true
  }
]
```

### GET `/api/learned`
Get topics the daughter has learned.

**Response:**
```json
[
  {
    "topic": "nursing",
    "fact_id": "nursing-01",
    "learned_at_age": 10,
    "date_learned": "2026-08-19T10:00:00"
  }
]
```

## Analytics

### GET `/api/analytics`
Get learning analytics and engagement metrics.

**Response:**
```json
{
  "topics": [
    {
      "topic": "nursing",
      "times_discussed": 5,
      "total_messages": 15,
      "messages_per_discussion": 3.0,
      "mastery_level": 3,
      "current_streak": 2,
      "first_discussed": "2026-08-10T10:00:00",
      "last_discussed": "2026-08-19T15:30:00"
    }
  ],
  "report": {
    "total_conversations": 42,
    "unique_topics": 3,
    "learning_efficiency": 0.75
  }
}
```

### GET `/api/recommendations`
Get personalized learning recommendations.

**Response:**
```json
{
  "recommendations": [
    "Review life_skills - only discussed once",
    "Push nursing from level 3 to 4"
  ]
}
```

## Advanced Insights

### GET `/api/insights`
Get comprehensive insights summary.

**Response:**
```json
{
  "emotional_trend": {
    "period_days": 7,
    "checkpoints": 5,
    "sentiment_distribution": {"positive": 3, "neutral": 2, "negative": 0},
    "avg_stress_level": 0.2
  },
  "learning_velocity": {
    "velocity": 1.5,
    "trend": "stable",
    "discussions_per_day": 1.5
  },
  "engagement_patterns": {
    "primary_interest": "nursing",
    "secondary_interests": ["finance"],
    "focus_level": "high"
  },
  "stress_indicators": [],
  "generated_at": "2026-08-19T16:00:00"
}
```

### GET `/api/insights/emotional-trend`
Get emotional patterns over time.

**Parameters:**
- `days` (optional) — Period in days (default: 7)

### GET `/api/insights/velocity`
Get learning pace metrics.

**Response:**
```json
{
  "velocity": 1.5,
  "trend": "stable",
  "discussions_per_day": 1.5,
  "days_active": 10
}
```

### GET `/api/insights/patterns`
Get engagement patterns.

**Response:**
```json
{
  "primary_interest": "nursing",
  "secondary_interests": ["finance", "life_skills"],
  "focus_level": "medium"
}
```

### GET `/api/insights/stress`
Get stress and disengagement indicators.

**Response:**
```json
{
  "indicators": [
    "High stress levels in recent conversations",
    "Learning pace is slowing down"
  ]
}
```

## Export & Backup

### GET `/api/export/conversations`
Export conversation history.

**Parameters:**
- `format` — "json" (default) or "csv"

**Response:** File download

### GET `/api/export/analytics`
Export analytics data.

**Response:** JSON file download

### GET `/api/export/knowledge-base`
Export knowledge base.

**Response:** JSON file download

### GET `/api/export/full-backup`
Export complete system backup.

**Response:** JSON file download (filename includes timestamp)

### GET `/api/export/summary`
Get backup summary without downloading.

**Response:**
```json
{
  "profile_name": "Sarah",
  "profile_age": 10,
  "total_conversations": 42,
  "topics_engaged": 3,
  "exported_at": "2026-08-19T16:00:00"
}
```

## PWA & Assets

### GET `/manifest.json`
PWA manifest for app installation.

### GET `/sw.js`
Service worker for offline caching.

## Error Handling

All endpoints return JSON with appropriate HTTP status codes:

| Code | Meaning |
|------|---------|
| 200  | OK |
| 400  | Bad request (invalid parameters) |
| 404  | Not found |
| 429  | Rate limited |
| 500  | Server error |

Error response format:
```json
{
  "error": "Description of what went wrong"
}
```

## Rate Limiting

- 100 requests per hour per IP
- 100 conversation turns per session
- Remaining requests returned in response headers

Check `/api/safety` for current rate limit status.
