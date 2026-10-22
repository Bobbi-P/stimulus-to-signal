# Deploy Stimulus to Signal to Vercel

The app is built with Python Dash. The folder `api/index.py` exposes Dash's
Flask/WSGI server to Vercel. `vercel.json` routes incoming requests (including
Dash callbacks and assets) to that function.

## Deploy through GitHub

1. Create a GitHub repository, for example `stimulus-to-signal`.
2. Upload the **contents of this folder** to the repository root. `app.py`,
   `model.py`, `requirements.txt`, `vercel.json`, `api/`, and `assets/` should
   all be visible at the root.
3. In Vercel, choose **Add New > Project** and import the GitHub repository.
4. Select **Other** if Vercel requests a framework preset, leave the root
   directory as `./`, and leave build/output commands unset.
5. Click **Deploy** and open the assigned `.vercel.app` URL.
6. Test all six graphs, stimulus and conductance sliders, Play/Pause, Step,
   Reset, and the comparison dropdown. Confirm that CSS loads.

## Deploy through Vercel CLI (alternative)

Install Node.js, then in this folder run:

    npm install -g vercel
    vercel
    vercel --prod

## Locally

    pip install -r requirements.txt
    python verify.py
    python app.py

Open http://127.0.0.1:8050

## Troubleshooting

- 404: Confirm `api/index.py` and `vercel.json` were uploaded, and that
  Vercel's project root is the directory containing them.
- Missing modules: Confirm `requirements.txt` is in the project root.
- Graphs don't update: Check Vercel Function logs for Python exceptions.
- Styles missing: The `assets/style.css` directory must be deployed.
- Slow responses: The Hodgkin-Huxley simulator uses pure Python time stepping
  for several traces per interaction; serverless cold starts and repeated
  calculations may be noticeable. Consider precomputing/cache optimization
  if performance becomes an issue.

This project is an educational simulation; the spatial traveling-wave view
is illustrative and not a complete cable-conduction model.
