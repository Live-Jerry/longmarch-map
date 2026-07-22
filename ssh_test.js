const { execSync } = require('child_process');
try {
  const result = execSync(
    'ssh -o StrictHostKeyChecking=accept-new -o ConnectTimeout=10 -o BatchMode=yes -i "' +
    process.env.USERPROFILE + '\\.ssh\\aliyun_ecs" root@8.133.203.255 "hostname && pwd && ls /root/"',
    { timeout: 20000, shell: 'cmd.exe', encoding: 'utf8' }
  );
  require('fs').writeFileSync('D:\\ssh_ok.txt', 'SUCCESS\n' + result);
} catch(e) {
  require('fs').writeFileSync('D:\\ssh_ok.txt', 'FAILED\n' + (e.stderr || e.message));
}
