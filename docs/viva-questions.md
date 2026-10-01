# Viva preparation

1. **What is NLP?** Computational analysis and processing of human language.
2. **Why is NLP needed here?** Complaints are free text; NLP extracts consistent searchable signals.
3. **What is tokenization?** Splitting text into units such as words.
4. **What are stop words?** Frequent function words with low topical value in many tasks.
5. **Why lemmatize?** It maps word forms toward a common base form.
6. **What is TF-IDF?** A term weight combining local frequency with inverse corpus frequency.
7. **Why TF-IDF?** It provides compact, explainable features for traditional text classification.
8. **What is Logistic Regression?** A linear classifier that estimates class probabilities.
9. **Why use it?** It is fast, understandable and effective for sparse text features.
10. **What is sentiment analysis?** Estimating positive, neutral or negative tone in text.
11. **What is classification?** Assigning an example to a predefined class.
12. **What is precision?** Correct positive predictions divided by all positive predictions.
13. **What is recall?** Found positive examples divided by all actual positives.
14. **What is F1?** The harmonic mean of precision and recall.
15. **What is overfitting?** Fitting training examples too closely and generalizing poorly.
16. **Why train/test split?** To estimate performance on held-out data.
17. **Why preprocess text?** It normalizes variants and reduces irrelevant feature differences.
18. **How is the source detected?** TF-IDF features are classified by a trained multiclass Logistic Regression model.
19. **How is severity calculated?** Transparent rules match intensity, duration, sleep and sensitive-context cues.
20. **How is urgency detected?** Critical severity or selected night-time/context phrases set a flag.
21. **Why SQLite?** It is local, serverless and suitable for a single-user prototype.
22. **Why FastAPI?** It supports typed request validation and automatic OpenAPI docs.
23. **How does the UI communicate with the API?** Browser fetch requests send and receive JSON over HTTP.
24. **What are the limitations?** Synthetic English data, small rule lexicons and uncalibrated scores.
25. **How could it improve?** Evaluate anonymized real data, add local languages, calibration and stronger auth.
26. **Why keep original text?** Auditability and comparison with the processed representation.
27. **What does confidence mean?** The model score for its winning label, not a calibrated guarantee.
28. **What is a confusion matrix?** A table comparing predicted and actual classes.
29. **Why stratify the split?** To preserve class proportions in train and test subsets.
30. **Does urgent mean a legal violation?** No, it is an informational triage signal only.
