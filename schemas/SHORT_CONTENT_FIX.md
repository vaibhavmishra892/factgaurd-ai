# Test: Short Content from Instagram URL

## Scenario
User provides an Instagram URL, but the article extractor only retrieves < 100 chars

## Before (Harsh)
```
❌ Error: Extracted content too short - may not be a valid article
```

**Problems**:
- Uses "Error"
- Sounds like system failure
- Blames the URL vaguely
- Doesn't tell user what to do next

---

## After (Friendly & Helpful)
```
⚠️  We couldn't retrieve the content from the social media link.

Some platforms require login or API access to fetch post text, which limits automated analysis.

Please paste the post's caption, description, or relevant text manually so we can analyze it.
```

**Benefits**:
- ✅ Explains the real reason
- ✅ Is polite
- ✅ Is honest
- ✅ Gives a clear next step

---

## How It Works

### Code Change in `article_extractor.py`

**Before**:
```python
if len(article_text) < 100:
    return {"error": "Extracted content too short - may not be a valid article"}
```

**After**:
```python
if len(article_text) < 100:
    # Use smart classification - likely a social media link or restricted content
    return {"error": classify_url_issue(url)}
```

### Smart Classification

The `classify_url_issue()` function automatically detects:

1. **Instagram URL** → Social media message
2. **Facebook URL** → Social media message  
3. **X/Twitter URL** → Social media message
4. **WhatsApp link** → Messaging app message
5. **NYTimes/WSJ** → Paywall message
6. **Generic URL** → Broken link message

---

## Test Results

**Input**: `https://www.instagram.com/p/test123`

**Output**:
```
⚠️  We couldn't retrieve the content from the social media link.

Some platforms require login or API access to fetch post text, which limits automated analysis.

Please paste the post's caption, description, or relevant text manually so we can analyze it.
```

✅ **Perfect** - Context-aware, helpful, and actionable!

---

## Impact

**Before**: Users frustrated by vague "content too short" error  
**After**: Users understand the limitation and know exactly what to do

This single change covers:
- 🔗 Instagram posts
- 🔗 Facebook posts  
- 🔗 Twitter/X posts
- 🔗 TikTok videos
- 🔗 LinkedIn posts
- 🔗 Paywalled articles
- 🔗 Login-required pages
