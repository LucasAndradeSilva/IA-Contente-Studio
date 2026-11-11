import {chromium} from 'playwright-core';
import {createServer} from 'node:http';
import {createReadStream,existsSync,mkdirSync} from 'node:fs';
import {extname,join,normalize,resolve,relative,isAbsolute} from 'node:path';
import {spawnSync} from 'node:child_process';

const [template='templates/video-models/css3d-coffee/index.html',output='outputs/cg-cafe-v2-001/prototypes/css3d.mp4',durationArg='8',fpsArg='30',previewTime]=process.argv.slice(2);
const duration=Number(durationArg),fps=Number(fpsArg),root=process.cwd(),frames=resolve(root,'work','render-frames',output.replace(/[^a-z0-9]+/gi,'-'));
mkdirSync(frames,{recursive:true});mkdirSync(resolve(output,'..'),{recursive:true});
const types={'.html':'text/html','.css':'text/css','.js':'text/javascript','.mjs':'text/javascript','.ttf':'font/ttf','.png':'image/png'};
const server=createServer((req,res)=>{let pathname;try{pathname=decodeURIComponent((req.url||'/').split('?')[0])}catch{res.writeHead(400);res.end();return}const file=normalize(join(root,pathname));const rel=relative(root,file);if(rel.startsWith('..')||isAbsolute(rel)||!existsSync(file)){res.writeHead(404);res.end();return}res.writeHead(200,{'Content-Type':types[extname(file)]||'application/octet-stream','Cache-Control':'no-store'});const stream=createReadStream(file);stream.on('error',()=>res.destroy());stream.pipe(res)});
await new Promise(ok=>server.listen(0,'127.0.0.1',ok));const port=server.address().port;
const browserPaths=['C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe','C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe','C:/Program Files/Google/Chrome/Application/chrome.exe'];const executablePath=browserPaths.find(existsSync);if(!executablePath)throw new Error('Brave, Edge ou Chrome não encontrado.');
const browser=await chromium.launch({headless:true,executablePath,args:['--disable-gpu-sandbox']});const page=await browser.newPage({viewport:{width:720,height:1280},deviceScaleFactor:1});await page.goto(`http://127.0.0.1:${port}/${template.replaceAll('\\','/')}`,{waitUntil:'networkidle'});await page.waitForFunction(()=>typeof window.renderAt==='function');
await page.evaluate(()=>document.fonts.ready);
if(previewTime!==undefined){await page.evaluate(t=>window.renderAt(t),Number(previewTime));await page.screenshot({path:resolve(output),animations:'disabled'});await browser.close();server.close();console.log(resolve(output));process.exit(0)}
for(let frame=0;frame<Math.round(duration*fps);frame++){await page.evaluate(t=>window.renderAt(t),frame/fps);await page.screenshot({path:join(frames,`${String(frame).padStart(5,'0')}.png`),animations:'disabled'});if(frame%60===0)process.stdout.write(`frame ${frame}/${Math.round(duration*fps)}\n`)}
await browser.close();server.close();const result=spawnSync('ffmpeg',['-y','-framerate',String(fps),'-i',join(frames,'%05d.png'),'-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',resolve(output)],{stdio:'inherit'});if(result.status!==0)process.exit(result.status||1);console.log(resolve(output));
