const fs = require("fs");
const path = require("path");

const structure = {
  contracts: ["issuer_whitelist.py", "certificate_nft.py"],
  backend: {
    "main.py": "",
    routes: {
      "issue.py": "",
      "verify.py": "",
    },
  },
  frontend: {
    src: {
      components: {},
      pages: {},
      "App.js": "",
    },
  },
  docs: {
    "architecture.md": "",
    "roadmap.md": "",
  },
  "README.md": `# SkillDCX 🚀
Decentralized Skill Certification on Algorand.

SkillDCX allows institutions to issue tamper-proof certificates, students to store them, and employers to instantly verify them — all on Algorand.

## Features
- Blockchain-based, tamper-proof certificates
- Issuer and student roles
- IPFS for decentralized file storage
- Open-source and extendable
  `,
  "CONTRIBUTING.md": `# Contributing to SkillDCX
Thanks for showing interest in contributing!

## Steps
1. Fork the repo
2. Create a feature branch
3. Commit changes
4. Push to your fork
5. Open a Pull Request
`,
  "LICENSE": `MIT License
Copyright (c) 2025 SkillDCX Contributors`,
  ".gitignore": `node_modules
__pycache__/
.env
`,
};

function createStructure(base, obj) {
  for (let key in obj) {
    const targetPath = path.join(base, key);

    if (typeof obj[key] === "string") {
      fs.writeFileSync(targetPath, obj[key]);
    } else if (typeof obj[key] === "object") {
      fs.mkdirSync(targetPath, { recursive: true });
      createStructure(targetPath, obj[key]);
    }
  }
}

createStructure(process.cwd(), structure);
console.log("✅ SkillDCX project structure created!");
