# Report: CV Parsing Implementation - Findings 

### 1. **PDF Parsing for Applicant CVs**:

* I was able to succcessfully implement the parsing of applicant **CVs (PDF files)**, with a focus on extracting key information from a pool of CVs sourced from peers.
* For the desired feature of **information capturing** from the uploaded files, the implementation is **feasible**. Its currently capable of extracting the **necessary fields** like **name, email, phone number, and address**, albeit with some caveats.

### 2. **Limitations and Variability**:

* **Accuracy of Parsing**: While most of the key fields are being captured with a degree of correctness, the results aren't perfect due to how different applicants can structure their CVs.

* **Work Experience Parsing**: The **major remaining issue** is the **work experience extraction**. Due to the high **variability** in how applicants format and encode their **work experience**, the system requires **significant manual review**. This variability includes different ways job titles, company names, and dates are presented, leading to **incorrect extractions** in some cases.

### 3. **Current Functionality**:

* The theoretical **user flow** would allow an applicant to upload a **PDF CV**. The system would parse the CV and **automatically fill in a number of fields** with **reasonably accurate data**. However, as mentioned, some fields may require review and correction due to the inconsistencies in parsing.
* As of now, the system provides **a good baseline** where key details like **contact information** and **work history** are extracted with a moderate degree of success, but **manual intervention** remains necessary for final accuracy.

### 4. **Further Refinement and Potential Challenges**:

* **Pattern Matching Refinement**: There is room for **further refinement** in the parsing logic, particularly in tightening regex patterns and improving the handling of sections. However, **over-strict pattern matching** may lead to **ignored fields** and may impede on the already functioning CV parsing.
* **Balance Between Precision and Flexibility**: While more stringent checks can improve accuracy, they could also create a more **rigid system** that may **not be as adaptable** to different CV layouts, potentially impeding productivity.

### 5. **Proof of Concept**:

* Overall, the **proof of concept** for the **information capture feature** has been **successful**. The **initial prototype** shows that it is feasible to extract key applicant details from **uploaded CVs** and input them into the system.
* While **manual review** is still required due to the inconsistencies in the parsing logic, the **core functionality** has been prototyped and validated.

## Conclusion

The **CV parsing feature** is now functional to a degree and allows **automatic information extraction** with a reasonable level of accuracy. My next step would be to start drafing the framework for the formal project which comprises this feature. 