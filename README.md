# DSO-576 setup test

This tiny project is part of the **DSO-576 laptop setup** — you clone it once
to prove that everything you installed actually works. It is **not** course
material: your weekly course repos appear on the course app's **HW page**
after the term starts.

Follow these steps exactly, one at a time, in your terminal.

## 1. Go to your course folder

You made a `dso576` folder during setup. Go there and check you're in it:

```
cd ~/dso576
pwd
```

`pwd` prints where you are — it should **end in `/dso576`**. If it doesn't,
run `cd ~/dso576` again.

## 2. Clone this repo (downloads it into the folder)

```
git clone https://github.com/pengshi-usc/00-setup.git
cd 00-setup
pwd
```

Now `pwd` should end in `/dso576/00-setup`.

## 3. Install the Python packages

```
uv sync
```

The first run downloads Python packages (this can take a minute or two —
lines of progress text are normal).

## 4. Run the test program

```
uv run hello.py
```

You should see a small table and then:
`SUCCESS — Python ... and pandas ... are working.`

## 5. Check every tool

```
bash check_setup.sh
```

Every line should say `PASS`. If a line says `FAIL`, it tells you exactly
which setup step to redo — fix it, then run `bash check_setup.sh` again
until everything passes.

## 6. See Streamlit run (we use it in class)

```
uv run streamlit hello
```

A demo app opens in your browser — that's Streamlit working. Back in the
terminal, press `Ctrl+C` to stop it.

That's it. When all checks pass, go back to the setup page and continue.
