# QUERY PANEL PLANNER (formerly ANSWER) — working rules for Claude Code

Single-file web app (`dist/index.html`, published as `index.html` on GitHub Pages from `main` of wesprojects/QUERY, site wesprojects.github.io/QUERY; renamed from ANSWER on 2026-09-26) that plans, specifies,
builds and installs Steelcase Answer panel systems from the **June 2022 Answer Solutions Specification Guide** (the source since 2026-09-25; the
February 2015 guide it replaced is kept for the citations still marked "2015 pNN"). Space planners use it live.

## The one rule that outranks everything
**Nothing may leave the specification guide.** Every style number, quantity, dimension, junction rule, support rule and option comes from the
guide, cited by page in a code comment. When a customer's system (CAP catalog, reman numbers) differs from the guide, keep the guide's numbers
and list the difference in the README for the owner to decide. Never rename, add or drop a part to make an export or an import work.
Never guess a dimension: read the page (`guide2022/pNNN.txt`, the PDFs `answer-2022-1.pdf` p1–189 and `answer-2022-2.pdf` p190–766, rendered with
pymupdf; the full `answer-2022.pdf` stays out of git). The 2015 text is `guide/pNNN.txt` (`answer-1.pdf` p1–200, `answer-2.pdf` p201–766). A citation written
`2015 pNN` is a 2015 page; every other `pNN` is a 2022 page.

## Layout
- `src/engine.js` rules, BOM, geometry, SIF, plain DXF; `src/capdxf.js` CAP DXF export; `src/planner.js` interface and drawing; `src/planner.html`,
  `src/planner.css`; `src/catalog.json` (156 products, 3,057 rows, 3,019 style numbers, every row cites its guide page).
- `build.py` writes `dist/index.html` (build number = New York date + counter; `--same` keeps the number). `build_catalog.py` and `build_workstations.py` are the
  2015 builders: never run `build_catalog.py` now (it reads a folder not in the repo and would write the 2015 catalog over `src/catalog.json`).
- `test/` — engine and Playwright tests. `cap/` — CAP format findings (`NOTES.md`), the R2000 skeleton (`tpl.js`, also `CAPDXF_TPL` in
  `src/capdxf.js`), the reference drawings (`ref_r2000.dxf`, `TEST_B2_one_workstation_cap_blocks.dxf`, `TEST_C_R2000.dxf`) and the render scripts
  (`render.py`, `svg2png.js`, `make_b2.py`).
- **The authoritative source is `source/` in this repo** (pushed from the cloud session 2026-09-24 at build .14 plus CLAUDE.md and the guide text).
  A local checkout that rebuilt from a stale zip must merge its own changes onto `source/`, not the other way round: diff first, keep both sides' work.
- `guide2022/pNNN.txt` — the 2022 guide's text by page, with the 2015-to-2022 page map (`_citemap.py`), the re-pricing reports and `_comparison.md`;
  `guide/pNNN.txt` — the 2015 text. Catalog update scripts, run in order: `update_catalog_2022.py`, `update_options_2022.py`, `add_rows_2022.py`,
  `hand_rows_2022.py`, `new_products_2022.py`, `review_fixes_2022.py` (the 2015 catalog they start from is `data/catalog_2015.json`; the chain rebuilds
  `src/catalog.json` exactly, so fix catalog data in a script, never by hand). `README.md` — the product description, the guide's rules as applied, corrections applied, tests.

## Facts already settled (do not re-derive or relitigate)
- In-line junction 1 1/2" along the run centred on the node (p30); end-of-run post 3/4" inside the module, trim 1/2" thin / 1" oval beyond (p20, p46, p92);
  skins run over straight junctions (p22); base trim 3 3/4" (p58, p59), top cap the 2 1/4" left of the 6" allowance (p19); thin cap drawn as its 5/8" lip; corner caps p388 (90° square 3",
  120° triangular, inradius 1.5/√3).
- Corner allowance: a panel off an L/T/X starts 1 1/2" from the corner centre (about 5/8" at V/Y); node-to-node = width + allowances; geometry
  normalised on every change (`E.normalizeGeometry`); CAP's own drawings confirm it.
- Worksurfaces butt with no gap; supports on junctions (p225, p236); tie plates at every seam, 3" in from the edge (p224, p237; the placement is from the 2015 p181–182 figures); one per cantilever/CSP,
  packs of 6 TS7TIEPLATE; cantilever 15 1/2" deep; CSP 11".
- Frameless glass thin only, 24"W and up, not over a top-position window, connector TS7TFGRC per p399, one glass kit may span in-line panels (p65).
- Worksurface ends hang on junctions (p225, p236), so an L of two straights needs the return leg segmented to put a junction at the other
  worksurface's front edge (24"W panel + 1 1/2" = 25 1/2" for a 24"D); 35 1/2"D straights are freestanding only (p540 tip), so 36"D is not offered on panels.
- The 2015 guide misprinted TS742SVPJW and TS742VPJ in the 48" V rows (2015 p400, p401); the 2022 guide prints TS748SVPJW and TS748VPJ (p436, p437), so no
  correction or flag remains. Grommet 6612 Grey V2 is marked E, "Established" (p727).
- Prices: `catalog.json` holds the printed June 2022 list; `E.init` adds the July 18, 2022 9% once (p1; owner, 2026-09-27), each price and option rounded on
  its own. Canadian list stays at 1.09 (owner). Recessed frameless glass: top of the pane the kit height above the cap, the rest in the cap slot (owner, 2026-09-28).
- The 6"H stacker: thin trim only; on a base junction only, never on a stacking junction (incl. the taller side of an in-line change of height, p357);
  its tier takes 6"H technology skins without cutouts (p139, p505) and no stacking frame package (p34).
- CAP DXF: CAP refuses R12; accepts R2000 (AC1015). Parts are `P_<style>` blocks with the 16 CAP attributes; panels are config blocks with the
  frame and skins nested; CAP keeps block definitions that are in the drawing (so correct `3_<style>` 3D blocks can ship in the file).
- CAP 3D (decoded from the owner's samples 2026-09-25): CAP's 3D view swaps each `P_<name>` insert for `3_<name>`; 3D bodies are polyface meshes on layers
  `AFUPA-3D-nnn` (panel parts) and `AFUSK-3D-nnn` (skins); a 3D config block nests the frame at the origin, skins at z = base trim on each face (side A on the
  y = 0 face turned 180°, side B on the y = 3 face), tiers and windows above. The export writes a `3_` twin for every `P_` block from the guide's dimensions
  (README "3D blocks in the CAP export"); skins and panes are faces because the guide prints no thickness. CAP rebuilds a panel's 3D graphics from
  the 2D config (nested symbol kept in place, swapped for its `3_` twin, lifted by CAPDH), so configs nest tiles exactly as CAP's do, bodies drawn from their own origin.

## Workflow — every change
1. Work in the source; add or extend a test for the change (a Playwright test for interface changes, `test/test.js` for rules).
2. Run the whole suite before any push: `node test/test.js`, then `NODE_PATH=$(npm root -g) node test/<name>.js` for
   ui3 ui5 ui6 ui7 ui8 ui9 ui10 ui11 ui2022 uireview guidex plan ws2 outputs wsoverlap wsstress final dims caps elevpick handle join corner capbtn overlap, and
   `node test/capdxf.js` and `node test/cap3d.js` (need `pip install ezdxf`). `overlap` must end `TOTAL 0`. Copy `answer-2022-1.pdf`, `answer-2022-2.pdf`, `answer-1.pdf` and `answer-2.pdf` into `dist/` for the guide tests.
   `bash test/run_all.sh` runs everything, prints one line per file and a total, and exits 1 if any file fails (every test file sets its exit code).
   On the owner's Windows machine (Git Bash): the project is `Desktop\ANSWER PANEL PLANNER` (this repo's checkout) and the tests run from `source\`;
   use `python` (`python3` is the Store stub; `pip install pymupdf ezdxf tzdata`), `export NODE_PATH="$(npm root -g)"`, copy the PDFs into `dist/`
   (symlinks need admin rights), and `build.py` writes LF so the built file matches the repo.
3. Update `README.md` (what changed and the guide pages behind it). Build with `python3 build.py`.
4. Commit the source (`source/` is part of this repo now; `dist/`, caches and test output stay ignored) with a clear message.
   Copy `dist/index.html` and `README.md` (and this file) into the repo checkout, commit, push to
   `claude/dazzling-gauss-0nzo38`, fast-forward `main` (`git checkout main && git merge --ff-only claude/dazzling-gauss-0nzo38 && git push`), so it goes live.
5. Zip the source (everything but `.git`, `__pycache__`, `test/overlap`, `test/capout`, `dist/*.pdf`, PNGs, `test/run_*.log`) to `Downloads\QUERY\QUERY_source.zip`.
6. Report plainly: what changed, what the tests showed, what is not done. No silent skips.

## Interface conventions the owner has set
Thin top cap thin; ends and junctions look like the real parts; ⊕ handles 20px, left-click extends straight, right-click lists compliant directions
only; Add worksurface tool with depth and width choices; dragging a run snaps onto another run only where Answer allows the junction; clicking a
part in an elevation centres the plan on it without scrolling the page; the hide/show editor control is « ».

## Open work (in order)
1. CAP 3D. For Steelcase parts CAP draws its own library bodies and ignores our `3_` twins (proved by the owner's CAP-saved DXF). The route is a Conklin
   catalog for CAP; that work (the catalog files, the vendor's package format, Auto Hardware) is private and lives outside this repo. Pedestals, supports
   and power parts are still points in the export.
2. Import CAP Worksheet exports / SIF / CAP DXF attributes as a job for the Pick & Install stage (waiting on worksheet exports and a pick list sample).
3. (Resolved 2026-09-25 with the 2022 guide: `E.GLASS.recessed.heights` is keyed 6/12/18/24 with 9 5/16", 15 1/2", 21 11/16", 27 7/8", p64.)
4. Place big open base skins and Answer boundary screens from the plan (in the catalog since the 2022 update, not yet in the interface).
5. Owner decisions still open: the 30"H wall-start conflict (p20 vs p372, flagged); reinforcing channel sizing (p217 span method vs the p224/p246 knife-edge
   rule the engine uses); the README items marked "Owner to decide". Decided: the 9% increase (applied), Canadian 1.09 (kept), glass height (recessed).
