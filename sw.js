/* ZK-88 offline support: keeps a copy of the app on the device.
   Online it fetches the latest version first (and refreshes the copy); offline it uses the copy. */
const CACHE='zk88-v9';
const bust=u=>{const x=new URL(u);x.searchParams.set('_',Date.now());return x.href};
const CORE=['./','index.html','manifest.webmanifest','fonts/fonts.css','fonts/Baloo2.woff2','fonts/PressStart2P-400.woff2',
  'icons/apple-touch-icon.png','icons/icon-192.png','icons/icon-512.png',
  ...['kick1','kick2','kick_soft','snare1','snare2','snare_mid','snare_ghost','hat','hat_soft','open','break',
    'horn_short','horn_long','boom','laser','coin','power'].map(n=>'samples/'+n+'.wav')];
self.addEventListener('install',e=>{e.waitUntil(caches.open(CACHE).then(c=>c.addAll(CORE)).then(()=>self.skipWaiting()))});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim()))});
self.addEventListener('fetch',e=>{
  const r=e.request;if(r.method!=='GET'||new URL(r.url).origin!==location.origin)return;
  const fromCache=()=>caches.match(r,{ignoreSearch:true}).then(m=>m||(r.mode==='navigate'?caches.match('index.html'):undefined));
  const p=new URL(r.url).pathname,fresh=r.mode==='navigate'||/\.(html|js|css|webmanifest)$/.test(p)||p.endsWith('/');
  const net=(fresh?fetch(bust(r.url),{cache:'no-store'}):fetch(r)).then(res=>{if(res.ok){const cp=res.clone();caches.open(CACHE).then(c=>c.put(r,cp))}return res});
  // wait up to 4 s for the network, then use the saved copy
  e.respondWith(Promise.race([net,new Promise(res=>setTimeout(()=>fromCache().then(m=>m&&res(m)),4000))]).catch(()=>fromCache()));
});
