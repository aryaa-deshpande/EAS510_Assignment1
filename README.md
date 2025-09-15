## HOW TO RUN:

**1. Create And Activate A Virtual Evironment:**
```
   python -m venv myenv
   source myenv/bin/activate 
```

**2. Install Dependencies:**
```
pip install pillow opencv-python ssdeep numpy
```

**3. Run The System:**
```
python test_system.py | tee results.txt
```

## WHAT I DID:
- Wrote an expert system (`SimpleDetective`) that tries to match modified images back to their originals.  
- Added three checks: file metadata, fuzzy hashing with ssdeep, and visual template matching with OpenCV.  
- Tested the code on 60 modified images and 5 random images.  

## WHAT I FOUND:
- The system worked really well for edits like brightness changes, compression, and PNG conversions.  
- Cropped images were harder — 75% crops matched sometimes, but 25% and 50% crops mostly failed.  
- The ssdeep rule didn’t really help here, which fits what we expected.  
- None of the random images were matched, which is good (no false positives).  

## KEY TAKEAWAYS:
This project showed how a rule-based system can combine simple pieces of evidence and still get decent results.  

---

