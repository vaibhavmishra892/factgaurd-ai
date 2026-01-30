# URL Response Messages - Quick Reference

## New URL-Specific Messages Added

### 1. Social Media Links
**Platforms**: Instagram, Facebook, X/Twitter, TikTok, LinkedIn, Threads

**Message**:
```
⚠️  We couldn't retrieve the content from the social media link.

Some platforms require login or API access to fetch post text, which limits automated analysis.

Please paste the post's caption, description, or relevant text manually so we can analyze it.
```

**Usage**:
```python
from schemas.response_messages import social_media_link_issue
return {"error": social_media_link_issue()}
```

---

### 2. Login-Required Links
**Triggers**: HTTP 401, 403 status codes

**Message**:
```
⚠️  We couldn't access the content from the provided link.

The page appears to require login or special access, which prevents content retrieval.

If possible, please share the visible text or use a publicly accessible source.
```

---

### 3. Paywalled Content
**Domains**: NYTimes, WSJ, FT, Economist, Bloomberg, Telegraph  
**Triggers**: HTTP 402, 451 status codes

**Message**:
```
⚠️  We couldn't retrieve the full content from the link.

The source appears to be restricted or paywalled, limiting access to the article text.

You may paste the relevant excerpt or use an alternative public source for analysis.
```

---

### 4. Broken/Expired Links
**Triggers**: HTTP 404, 410 status codes

**Message**:
```
⚠️  We couldn't retrieve content from the provided link.

The link may be broken, expired, or no longer available.

Please check the link or share the content text directly.
```

---

### 5. Messaging App Forwards
**Links**: wa.me, WhatsApp, Telegram (t.me)

**Message**:
```
ℹ️  The link appears to reference forwarded or informal content.

Such sources often lack verifiable context or public access.

Please paste the message text or provide a reliable external source for verification.
```

---

## Smart Classification

The system automatically detects the appropriate message using `classify_url_issue()`:

```python
from schemas.response_messages import classify_url_issue

# Automatically selects the right message
response = classify_url_issue(
    url="https://instagram.com/post",
    status_code=403,
    error_type="ConnectionError"
)
```

**Detection Priority**:
1. Social media platforms (by domain)
2. Messaging apps (by domain)
3. HTTP status codes (401, 403, 404, 410, 402, 451)
4. Known paywall domains
5. Error type (timeout, connection)
6. Default: broken link

---

## Integration

### article_extractor.py
```python
except requests.exceptions.HTTPError as e:
    status_code = e.response.status_code if e.response else None
    return {"error": classify_url_issue(url, status_code=status_code)}

except Exception as e:
    return {"error": classify_url_issue(url, error_type=str(e))}
```

---

## Test Results

✅ **All 5 message types tested**  
✅ **URL classification working**  
✅ **HTTP status code detection working**  
✅ **No forbidden words found**  
✅ **All messages include helpful suggestions**

**Quality Checks**:
- Message 1-5: PASS - Has helpful suggestion
- All messages use: "Please paste", "share", "use", "try"
- No harsh language: error, failed, invalid, blocked
