#!/usr/bin/env node
/**
 * ci-scan.js — called by the GitHub Actions workflow to run SAST + CVE checks
 * on a comma-separated list of skill names passed as argv[2].
 *
 * WHY a separate script rather than inline shell: we want to reuse the
 * scanSkillSecurity() function from cli.js verbatim so CI and local CLI
 * are always in sync, and produce a structured Markdown report for the
 * PR comment step.
 */

const fs = require('fs');
const path = require('path');
const { scanSkillSecurity, sandboxTestSkill } = require('../src/cli.js');

const LOCAL_SKILLS_DIR = path.join(__dirname, '..', 'skills');
const REPORT_PATH = path.join(process.cwd(), 'security-report.md');

const skillsArg = process.argv[2] || '';
const skills = skillsArg.split(',').map(s => s.trim()).filter(Boolean);

if (skills.length === 0) {
  console.log('No skills to scan.');
  // Write an empty report so the comment step has a file to read.
  fs.writeFileSync(REPORT_PATH, '_No changed skills detected in this PR._\n');
  process.exit(0);
}

let overallPassed = true;
let report = '';

skills.forEach(skill => {
  const srcDir = path.join(LOCAL_SKILLS_DIR, skill);
  if (!fs.existsSync(srcDir)) {
    report += `### \`${skill}\`\n> ⚠️ Directory not found — skipping.\n\n`;
    return;
  }

  console.log(`\nScanning skill: ${skill}`);
  const result = scanSkillSecurity(srcDir);

  if (result.passed) {
    console.log(`  ✅ PASSED`);
    report += `### \`${skill}\` — ✅ PASSED\n`;
    report += `No security violations detected.\n\n`;
  } else {
    console.error(`  ❌ FAILED`);
    result.violations.forEach(v => console.error(`    • ${v}`));
    overallPassed = false;
    report += `### \`${skill}\` — ❌ FAILED\n`;
    report += `| Severity | Violation |\n|---|---|\n`;
    allViolations.forEach(v => {
      // WHY: Derive a rough severity tag from the violation category prefix.
      const severity = v.startsWith('[CVE]') ? '🔴 HIGH/CRITICAL' :
                       v.startsWith('[SYMLINK]') ? '🔴 CRITICAL' :
                       v.startsWith('[SANDBOX]') ? '🔴 CRITICAL' : '🟠 MEDIUM';
      report += `| ${severity} | ${v.replace(/^\[\w+\]\s*/, '')} |\n`;
    });
    report += `\n> ❌ **Installation blocked.** A maintainer must review and either fix the violations or explicitly approve with justification.\n\n`;
  }
});

// WHY: Append a summary line to aid quick triage.
report += `---\n**Overall result:** ${overallPassed ? '✅ All scans passed' : '❌ One or more scans failed'}\n`;

fs.writeFileSync(REPORT_PATH, report, 'utf8');
console.log(`\nReport written to ${REPORT_PATH}`);

// WHY: Non-zero exit triggers continue-on-error in Actions and is checked
// by the final "Fail if security violations found" step.
process.exit(overallPassed ? 0 : 1);
