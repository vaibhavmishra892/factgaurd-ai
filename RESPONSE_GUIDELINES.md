# User-Facing Response Guidelines

## Purpose
This document explains how the system communicates verification outcomes to users in a polite, clear, and trust-preserving manner.

---

## Core Principles

All responses MUST:
- ✅ Be polite and neutral
- ✅ Acknowledge that the input was processed successfully
- ✅ Clearly explain why verification was not performed
- ✅ Avoid technical blame or harsh language
- ✅ Preserve system credibility

---

## Response Categories

### 1️⃣ No Explicit Factual Claim Found

**When**: Images with tables, posters with slogans, headlines without assertions

**Message**:
```
ℹ️ Content Reviewed Successfully

We reviewed the content successfully, but didn't find a clear factual 
statement that can be independently verified.
```

**Usage**:
```python
from schemas.response_messages import OutcomeCategory, format_unverifiable_response

return format_unverifiable_response(OutcomeCategory.NO_FACTUAL_CLAIM)
```

---

### 2️⃣ Time-Sensitive / Real-Time Data

**When**: Gold prices, stock prices, weather snapshots

**Message**:
```
ℹ️ Time-Sensitive Data Detected

The content was analyzed successfully. It appears to contain 
time-sensitive information that changes frequently.
```

**Usage**:
```python
from schemas.response_messages import time_sensitive_data

return time_sensitive_data()
```

---

### 3️⃣ Opinion or Predictive Statement

**When**: "This will be the biggest scam", "India will become..."

**Message**:
```
ℹ️ Opinion or Prediction Identified

The statement appears to express an opinion or a future prediction 
rather than a verifiable factual claim.
```

**Usage**:
```python
from schemas.response_messages import opinion_detected

return opinion_detected()
```

---

### 4️⃣ Insufficient Context

**When**: Partial sentences, cropped images, ambiguous claims

**Message**:
```
ℹ️ Additional Context Needed

We analyzed the input, but there wasn't enough clear context to 
reliably verify the information.
```

**Usage**:
```python
from schemas.response_messages import insufficient_context

return insufficient_context()
```

---

### 5️⃣ Source-Dependent Claim

**When**: "According to a WhatsApp forward...", "This post claims..."

**Message**:
```
ℹ️ Informal Source Detected

The claim depends on an unspecified or informal source, making 
independent verification unreliable.
```

**Usage**:
```python
from schemas.response_messages import OutcomeCategory, format_unverifiable_response

return format_unverifiable_response(OutcomeCategory.SOURCE_DEPENDENT)
```

---

### 6️⃣ Technical Processing Issue

**When**: OCR failed, image unreadable, network error

**Message**:
```
⚠️ Processing Issue Encountered

We attempted to analyze the content, but encountered a technical 
issue during processing.
```

**Usage**:
```python
from schemas.response_messages import ocr_failed, network_error

# For OCR failures
return ocr_failed()

# For network issues
return network_error("Connection timeout")
```

---

## Integration Examples

### Example 1: No Claims in Image
```python
from schemas.response_messages import no_claims_in_image

# In input_router.py
if not claims:
    return {"error": no_claims_in_image()}
```

### Example 2: OCR Failure
```python
from schemas.response_messages import ocr_failed

# In image_text_extractor.py
if tesseract_not_found:
    return {"error": ocr_failed("Tesseract OCR not installed")}
```

### Example 3: Article Extraction Timeout
```python
from schemas.response_messages import format_extraction_error

# In article_extractor.py
except requests.exceptions.Timeout:
    return {"error": format_extraction_error("timeout")}
```

---

## Strictly Avoid These Phrases

❌ "Invalid input"  
❌ "Claim is unverifiable"  
❌ "Verification failed"  
❌ "Incorrect format"  
❌ "No valid claims"  
❌ "System error" (unless it truly is one)

These sound accusatory or broken.

---

## Response Style Guidelines

1. **Start with acknowledgment, not refusal**
   - ✅ "We reviewed the content successfully..."
   - ❌ "Invalid input detected"

2. **Use softening language**
   - Use "appears to", "may", "currently"
   - Avoid absolute statements

3. **Provide helpful guidance**
   - Suggest alternatives
   - Explain system limitations

4. **Keep tone calm and respectful**
   - Never blame the user
   - Maintain professional demeanor

---

## Success Checklist

Before finalizing a response, verify:

- ✅ Does it sound polite?
- ✅ Does it avoid blaming the user?
- ✅ Does it explain why verification wasn't done?
- ✅ Does it avoid guessing correctness?
- ✅ Does it preserve trust?

---

## Future Enhancements

Consider adding:
- Localization support for multiple languages
- Severity levels for different error types
- User feedback collection mechanisms
- Contextual help links
