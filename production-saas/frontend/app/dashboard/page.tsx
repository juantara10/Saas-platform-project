"use client";

import {FormEvent,useEffect,useMemo,useState} from "react";
import {api,API} from "../../lib/api";
import {useRouter} from "next/navigation";

type Org={id:string,name:string,slug:string};
type Member={user_id:string,email:string,role:string};
type Key={id:string,name:string,prefix:string,created_at:string};
type Log={action:string,metadata:Record<string,unknown>|null,created_at:string};
type Tab="overview"|"organizations"|"team"|"keys"|"analytics"|"audit"|"billing"|"settings";

const nav:[Tab,string,string][]=[
 ["overview","Overview","⌂"],["organizations","Organizations","◇"],["team","Team & RBAC","◎"],
 ["keys","API Keys","⌘"],["analytics","Analytics","↗"],["audit","Audit Logs","≡"],
 ["billing","Billing","$"],["settings","Settings","⚙"]
];

export default function Dashboard(){
 const router=useRouter();
 const [tab,setTab]=useState<Tab>("overview"),[orgs,setOrgs]=useState<Org[]>([]),[email,setEmail]=useState("Loading…");
 const [active,setActive]=useState(""),[members,setMembers]=useState<Member[]>([]),[keys,setKeys]=useState<Key[]>([]),[logs,setLogs]=useState<Log[]>([]);
 const [err,setErr]=useState(""),[notice,setNotice]=useState(""),[orgName,setOrgName]=useState(""),[keyName,setKeyName]=useState("Production API");
 const [inviteEmail,setInviteEmail]=useState(""),[inviteRole,setInviteRole]=useState("member"),[newKey,setNewKey]=useState("");

 const org=useMemo(()=>orgs.find(o=>o.id===active)||orgs[0],[orgs,active]);
 async function loadBase(){try{const [u,o]=await Promise.all([api("/api/v1/users/me"),api("/api/v1/organizations")]);setEmail(u.email);setOrgs(o);if(o[0]&&!active)setActive(o[0].id)}catch(e:any){setErr(e.message)}}
 async function loadOrg(id:string){if(!id)return;setErr("");const h={"X-Organization-ID":id};const results=await Promise.allSettled([api(`/api/v1/organizations/${id}/members`),api("/api/v1/api-keys",{headers:h}),api("/api/v1/audit-logs",{headers:h})]);if(results[0].status==="fulfilled")setMembers(results[0].value);if(results[1].status==="fulfilled")setKeys(results[1].value);if(results[2].status==="fulfilled")setLogs(results[2].value)}
 useEffect(()=>{loadBase()},[]);
 useEffect(()=>{if(active)loadOrg(active)},[active]);

 function flash(s:string){setNotice(s);setTimeout(()=>setNotice(""),3500)}
 async function createOrg(e:FormEvent){e.preventDefault();if(!orgName.trim())return;try{const o=await api("/api/v1/organizations",{method:"POST",body:JSON.stringify({name:orgName})});setOrgs(v=>[...v,o]);setActive(o.id);setOrgName("");flash("Organization created");}catch(e:any){setErr(e.message)}}
 async function invite(e:FormEvent){e.preventDefault();if(!org)return;try{await api(`/api/v1/organizations/${org.id}/members`,{method:"POST",body:JSON.stringify({email:inviteEmail,role:inviteRole})});setInviteEmail("");await loadOrg(org.id);flash("Member added");}catch(e:any){setErr(e.message)}}
 async function createKey(e:FormEvent){e.preventDefault();if(!org)return;try{const k=await api("/api/v1/api-keys",{method:"POST",headers:{"X-Organization-ID":org.id},body:JSON.stringify({name:keyName})});setNewKey(k.api_key);await loadOrg(org.id);flash("API key created");}catch(e:any){setErr(e.message)}}
 async function checkout(){if(!org)return;try{const r=await api("/api/v1/billing/checkout",{method:"POST",body:JSON.stringify({organization_id:org.id})});location.href=r.url}catch(e:any){setErr(e.message)}}
 function logout(){localStorage.removeItem("token");router.push("/login")}

 const role=members.find(m=>m.email===email)?.role||"member";
 return <div className="app">
  <aside className="sidebar">
   <div className="logo"><span className="logoMark">A</span><div><b>ATLAS</b><small>Cloud workspace</small></div></div>
   <nav className="sideNav">{nav.map(([id,label,icon])=><button key={id} className={tab===id?"active":""} onClick={()=>setTab(id)}><span>{icon}</span>{label}</button>)}</nav>
   <div className="sideFoot"><div className="statusDot"><i/> Production API</div><button onClick={logout}>Sign out</button></div>
  </aside>
  <main className="content">
   <header className="topbar"><div><span className="eyebrow">{org?.name||"Workspace"}</span><b>{title(tab)}</b></div><div className="topActions"><a href={`${API}/docs`} target="_blank">API Docs ↗</a><span className="avatar">{email[0]?.toUpperCase()}</span><span className="user">{email}<small>{role}</small></span></div></header>
   <section className="page">
    {err&&<div className="alert error">{err}<button onClick={()=>setErr("")}>×</button></div>}{notice&&<div className="alert success">{notice}</div>}
    {tab==="overview"&&<Overview orgs={orgs} members={members} keys={keys} logs={logs} org={org} setTab={setTab}/>}
    {tab==="organizations"&&<Organizations orgs={orgs} active={org?.id||""} setActive={setActive} orgName={orgName} setOrgName={setOrgName} createOrg={createOrg}/>}
    {tab==="team"&&<Team members={members} inviteEmail={inviteEmail} setInviteEmail={setInviteEmail} inviteRole={inviteRole} setInviteRole={setInviteRole} invite={invite}/>}
    {tab==="keys"&&<Keys keys={keys} keyName={keyName} setKeyName={setKeyName} createKey={createKey} newKey={newKey}/>}
    {tab==="analytics"&&<Analytics logs={logs} keys={keys} members={members}/>}
    {tab==="audit"&&<Audit logs={logs}/>}
    {tab==="billing"&&<Billing checkout={checkout}/>}
    {tab==="settings"&&<Settings email={email} org={org} role={role}/>}
   </section>
  </main>
 </div>
}

function title(t:Tab){return ({overview:"Workspace overview",organizations:"Organizations",team:"Team & access",keys:"Developer API keys",analytics:"Workspace analytics",audit:"Security audit log",billing:"Plans & billing",settings:"Workspace settings"} as Record<Tab,string>)[t]}

function Heading({kicker,title,copy}:{kicker:string,title:string,copy:string}){return <div className="heading"><span>{kicker}</span><h1>{title}</h1><p>{copy}</p></div>}
function Overview({orgs,members,keys,logs,org,setTab}:{orgs:Org[],members:Member[],keys:Key[],logs:Log[],org?:Org,setTab:(t:Tab)=>void}){return <><Heading kicker="LIVE WORKSPACE" title="Everything your team needs to ship securely." copy="A production SaaS control plane for organizations, access, developer credentials, billing and security events."/><div className="metrics"><Metric label="Organizations" value={String(orgs.length)} hint="Multi-tenant workspaces"/><Metric label="Team members" value={String(members.length)} hint="Role-based access"/><Metric label="API keys" value={String(keys.length)} hint="Scoped credentials"/><Metric label="API status" value="Healthy" hint="Railway production"/></div><div className="twoCol"><section className="panel"><div className="panelHead"><div><span className="eyebrow">ACTIVITY</span><h2>Recent events</h2></div><button className="linkBtn" onClick={()=>setTab("audit")}>View all →</button></div>{logs.length?logs.slice(0,5).map((l,i)=><div className="event" key={i}><span className="eventIcon">✓</span><div><b>{pretty(l.action)}</b><small>{date(l.created_at)}</small></div></div>):<Empty text="Actions in this workspace will appear here."/>}</section><section className="panel"><span className="eyebrow">CURRENT WORKSPACE</span><h2>{org?.name||"No organization"}</h2><p className="muted">/{org?.slug}</p><div className="stack"><button className="primary" onClick={()=>setTab("team")}>Manage team</button><button className="secondary" onClick={()=>setTab("keys")}>Create API key</button></div><div className="security"><b>Tenant isolation enabled</b><p>Requests are scoped by organization and protected with JWT + RBAC.</p></div></section></div></>}
function Metric({label,value,hint}:{label:string,value:string,hint:string}){return <article className="metricCard"><span>{label}</span><strong>{value}</strong><small>{hint}</small></article>}
function Organizations({orgs,active,setActive,orgName,setOrgName,createOrg}:any){return <><Heading kicker="MULTI-TENANCY" title="Organizations" copy="Create isolated workspaces and switch between tenants."/><div className="twoCol"><section className="panel"><h2>Your workspaces</h2>{orgs.map((o:Org)=><button className={"orgRow "+(o.id===active?"selected":"")} key={o.id} onClick={()=>setActive(o.id)}><span className="orgBadge">{o.name[0]}</span><span><b>{o.name}</b><small>/{o.slug}</small></span><i>{o.id===active?"Active":"Switch"}</i></button>)}</section><section className="panel"><h2>Create organization</h2><p className="muted">Start another isolated tenant workspace.</p><form className="form" onSubmit={createOrg}><input className="input" placeholder="Acme Inc." value={orgName} onChange={(e:any)=>setOrgName(e.target.value)}/><button className="primary">Create workspace</button></form></section></div></>}
function Team({members,inviteEmail,setInviteEmail,inviteRole,setInviteRole,invite}:any){return <><Heading kicker="RBAC" title="Team & access" copy="Demonstrate owner, admin, member and viewer authorization."/><section className="panel"><div className="panelHead"><h2>Members</h2><span className="count">{members.length} users</span></div><div className="table"><div className="tr th"><span>User</span><span>Role</span><span>Access</span></div>{members.map((m:Member)=><div className="tr" key={m.user_id}><span><b>{m.email}</b><small>{m.user_id.slice(0,8)}…</small></span><span><em className={"role "+m.role}>{m.role}</em></span><span>{m.role==="owner"?"Full control":m.role==="admin"?"Manage workspace":m.role==="viewer"?"Read only":"Standard"}</span></div>)}</div></section><section className="panel compact"><h2>Add registered user</h2><form className="inlineForm" onSubmit={invite}><input className="input" type="email" placeholder="teammate@example.com" value={inviteEmail} onChange={(e:any)=>setInviteEmail(e.target.value)}/><select className="input" value={inviteRole} onChange={(e:any)=>setInviteRole(e.target.value)}><option>admin</option><option>member</option><option>viewer</option></select><button className="primary">Add member</button></form><p className="hint">Demo safeguard: the user must register before being added.</p></section></>}
function Keys({keys,keyName,setKeyName,createKey,newKey}:any){return <><Heading kicker="DEVELOPER PLATFORM" title="API keys" copy="Issue organization-scoped credentials without exposing stored secrets."/><section className="panel compact"><form className="inlineForm" onSubmit={createKey}><input className="input" value={keyName} onChange={(e:any)=>setKeyName(e.target.value)} placeholder="Key name"/><button className="primary">+ Create API key</button></form>{newKey&&<div className="secret"><b>Copy this key now — it will not be shown again.</b><code>{newKey}</code></div>}</section><section className="panel"><div className="table"><div className="tr th"><span>Name</span><span>Prefix</span><span>Created</span></div>{keys.map((k:Key)=><div className="tr" key={k.id}><span><b>{k.name}</b></span><span><code>{k.prefix}••••••••</code></span><span>{date(k.created_at)}</span></div>)}</div>{!keys.length&&<Empty text="No API keys yet. Create one above."/>}</section></>}
function Analytics({logs,keys,members}:{logs:Log[],keys:Key[],members:Member[]}){const actions=logs.reduce((a,l)=>(a[l.action]=(a[l.action]||0)+1,a),{} as Record<string,number>);const max=Math.max(1,...Object.values(actions));return <><Heading kicker="REAL WORKSPACE DATA" title="Analytics" copy="Live operational counts derived from this workspace — no fabricated traffic metrics."/><div className="metrics"><Metric label="Audit events" value={String(logs.length)} hint="Latest 100 retained"/><Metric label="Active credentials" value={String(keys.length)} hint="API keys"/><Metric label="Members" value={String(members.length)} hint="Across RBAC roles"/><Metric label="Tracked actions" value={String(Object.keys(actions).length)} hint="Distinct event types"/></div><section className="panel"><h2>Activity by event type</h2>{Object.entries(actions).length?Object.entries(actions).map(([a,n])=><div className="barRow" key={a}><span>{pretty(a)}</span><div><i style={{width:`${Math.max(8,n/max*100)}%`}}/></div><b>{n}</b></div>):<Empty text="Create organizations, members or API keys to generate analytics."/>}</section></>}
function Audit({logs}:{logs:Log[]}){return <><Heading kicker="SECURITY & COMPLIANCE" title="Audit log" copy="Review privileged actions recorded for the active tenant."/><section className="panel">{logs.length?logs.map((l,i)=><div className="auditRow" key={i}><span className="eventIcon">✓</span><div><b>{pretty(l.action)}</b><small>{l.metadata?JSON.stringify(l.metadata):"No additional metadata"}</small></div><time>{date(l.created_at)}</time></div>):<Empty text="No audit events recorded yet."/>}</section></>}
function Billing({checkout}:{checkout:()=>void}){return <><Heading kicker="STRIPE BILLING" title="Plans that scale with your team." copy="The upgrade flow connects to Stripe Checkout when production billing credentials are configured."/><div className="plans"><Plan name="Demo" price="$0" features={["1 workspace","RBAC demonstration","Developer API access"]}/><Plan name="Pro" price="$29" featured features={["Unlimited workspaces","Advanced roles","Audit history","Stripe customer portal"]} action={checkout}/><Plan name="Business" price="Custom" features={["SSO/SAML ready","Priority support","Custom limits"]}/></div></>}
function Plan({name,price,features,featured,action}:any){return <article className={"plan "+(featured?"featured":"")}><span className="eyebrow">{featured?"RECOMMENDED":"PLAN"}</span><h2>{name}</h2><strong>{price}</strong>{price.startsWith("$")&&<small>/ month</small>}<ul>{features.map((x:string)=><li key={x}>✓ {x}</li>)}</ul>{action&&<button className="primary" onClick={action}>Upgrade with Stripe</button>}</article>}
function Settings({email,org,role}:{email:string,org?:Org,role:string}){return <><Heading kicker="ACCOUNT" title="Workspace settings" copy="Inspect the identity and tenant context used by the live API."/><div className="twoCol"><section className="panel"><h2>Profile</h2><label>Email</label><div className="readOnly">{email}</div><label>Workspace role</label><div className="readOnly">{role}</div></section><section className="panel"><h2>Organization context</h2><label>Name</label><div className="readOnly">{org?.name}</div><label>Organization ID</label><div className="readOnly mono">{org?.id}</div><p className="hint">Used as X-Organization-ID for tenant-scoped API operations.</p></section></div></>}
function Empty({text}:{text:string}){return <div className="empty">{text}</div>}
function pretty(s:string){return s.replaceAll("_"," ").replaceAll("."," · ").replace(/\b\w/g,c=>c.toUpperCase())}
function date(s:string){return new Date(s).toLocaleString(undefined,{month:"short",day:"numeric",hour:"numeric",minute:"2-digit"})}
