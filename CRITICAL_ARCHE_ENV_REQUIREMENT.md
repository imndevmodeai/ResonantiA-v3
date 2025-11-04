# ⚠️ CRITICAL: ArchE Virtual Environment Requirement

## 🔴 MANDATORY FOR ALL PYTHON OPERATIONS

**ALL ArchE Python scripts MUST be executed within the `arche_env` virtual environment.**

## ✅ Correct Usage

```bash
# ALWAYS activate arche_env first
source arche_env/bin/activate

# Then run any ArchE Python script
python3 script_name.py
```

Or as a one-liner:

```bash
source arche_env/bin/activate && python3 script_name.py
```

## ❌ Incorrect Usage

```bash
# WRONG - No environment activation
python3 script_name.py

# WRONG - Wrong environment name
source arche_tual/bin/activate  # This doesn't exist!

# WRONG - Using 'python' instead of 'python3'
python script_name.py
```

## 📋 Key Scripts That Require arche_env

- `practice_novel_skill_combinations.py` - Novel skill practice
- `ask_arche_enhanced_v2.py` - Enhanced ArchE query interface
- `ask_arche.py` - Basic ArchE interface
- Any script importing from `Three_PointO_ArchE/`
- Any workflow execution scripts

## 🔍 Why This Matters

The `arche_env` virtual environment contains:
- All required Python packages
- Correct versions of dependencies
- ArchE-specific configurations
- API keys and environment variables

**Without activating arche_env, ArchE components will not function correctly.**

## 🛠️ Troubleshooting

If you see errors like:
- `No module named 'X'`
- `ImportError`
- `ModuleNotFoundError`

**First check**: Did you activate `arche_env`?

```bash
# Check if environment is active (look for (arche_env) prefix)
echo $VIRTUAL_ENV

# Should output: /mnt/3626C55326C514B1/Happier/arche_env
```

## 📝 Remember

**Before EVERY Python command, always:**

1. Navigate to project root: `cd /mnt/3626C55326C514B1/Happier`
2. Activate environment: `source arche_env/bin/activate`
3. Run script: `python3 <script_name>.py`

---

**This is a critical operational requirement for ArchE's proper functioning.**

