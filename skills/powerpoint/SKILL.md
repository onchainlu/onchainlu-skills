---
name: powerpoint
description: Create, read, edit .pptx decks with python-pptx.
license: MIT
metadata:
  hermes:
    tags: [pptx, powerpoint, presentations, slides, office, python-pptx]
    category: productivity
    related_skills: [docx, xlsx, pdf]
---

# PowerPoint Skill — Canonical Route Notice

This duplicate skill copy is stale. The maintained canonical PowerPoint skill and scripts are at `/opt/data/skills/productivity/powerpoint`. Use that directory for every PowerPoint operation; do not use scripts from this `.hermes` copy or its legacy `scripts/office/validate.py` and `scripts/office/soffice.py` routes.

## Required Routing

Run all create, read, edit, and render commands with the maintained scripts:

```bash
python /opt/data/skills/productivity/powerpoint/scripts/pptx_create.py spec.json out.pptx
python /opt/data/skills/productivity/powerpoint/scripts/pptx_read.py out.pptx --outline
python /opt/data/skills/productivity/powerpoint/scripts/pptx_read.py out.pptx --notes
python /opt/data/skills/productivity/powerpoint/scripts/pptx_edit.py out.pptx --replace-text OLD NEW --output edited.pptx
python /opt/data/skills/productivity/powerpoint/scripts/pptx_render.py edited.pptx --outdir render
```

The canonical scripts print JSON and return non-zero on failure. Consult the maintained skill at `/opt/data/skills/productivity/powerpoint/SKILL.md` for prerequisites, supported options, procedures, pitfalls, and verification requirements.
