# Quick Response Message Examples

## Import
```python
from schemas.response_messages import (
    no_claims_in_image,
    no_claims_in_article,
    time_sensitive_data,
    opinion_detected,
    insufficient_context,
    ocr_issue,
    network_issue,
    timeout_issue,
    classify_and_respond  # Smart classifier
)
```

---

## Common Scenarios

### 1. No Claims Found in Image
```python
# In input_router.py _process_image()
if not claims:
    return {"error": no_claims_in_image()}
```

### 2. No Claims Found in Article
```python
# In input_router.py _process_url()
if not claims:
    return {"error": no_claims_in_article()}
```

### 3. OCR Failed
```python
# In image_text_extractor.py
if not extracted_text:
    return {"error": ocr_issue()}
```

### 4. Network Error
```python
# In article_extractor.py
except requests.exceptions.ConnectionError:
    return {"error": network_issue()}
```

### 5. Timeout
```python
# In article_extractor.py
except requests.exceptions.Timeout:
    return {"error": timeout_issue()}
```

---

## Smart Classification (Recommended)

Instead of hardcoded responses, use the smart classifier:

```python
# In input_router.py _process_image()
if not claims:
    # Automatically detects: opinion, time-sensitive, or generic
    return {"error": classify_and_respond(ocr_text, "image")}

# In input_router.py _process_url()
if not claims:
    return {"error": classify_and_respond(article_text, "article")}
```

The classifier detects:
- Opinions ("will", "should", "think")
- Time-sensitive data ("price", "stock", "today")
- Informal sources ("whatsapp", "forward")
- Short/unclear text (< 10 chars)

---

## All Available Functions

| Function | Use Case |
|----------|----------|
| `no_claims_in_image()` | Image has no factual claims |
| `no_claims_in_article()` | Article has no factual claims |
| `no_claims_in_text()` | Text has no factual claims |
| `time_sensitive_data()` | Price/stock/live data |
| `opinion_detected()` | Opinion or prediction |
| `insufficient_context()` | Unclear/incomplete input |
| `informal_source()` | WhatsApp forward, rumor |
| `ocr_issue()` | OCR extraction failed |
| `network_issue()` | Connection error |
| `timeout_issue()` | Request timed out |
| `tesseract_missing()` | OCR engine not installed |
| `classify_and_respond(text, type)` | Auto-detect reason |

---

## Example Outputs

### No Claims (Image)
```
ℹ️ Image analyzed successfully.

We couldn't find a clear factual statement 
that can be independently verified.

The content appears to be informational or 
structured data, which is currently outside 
the scope of factual claim verification.
```

### Time-Sensitive Data
```
ℹ️ Image reviewed successfully.

It appears to contain time-sensitive information 
that changes frequently.

Verifying this type of data requires real-time 
authoritative sources, which this system does 
not currently use.
```

### Opinion Detected
```
ℹ️ Content processed successfully.

The statement appears to express an opinion or 
a future prediction rather than a factual claim 
that can be verified.
```

