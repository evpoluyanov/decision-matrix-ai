(() => {
 const toggle = document.querySelector('.menu-toggle'), menu = document.getElementById('decision-menu');
 if (!toggle || !menu) return;
 function close(focus) {menu.hidden = true; toggle.setAttribute('aria-expanded','false'); if(focus) toggle.focus();}
 toggle.addEventListener('click',()=>{menu.hidden=!menu.hidden;toggle.setAttribute('aria-expanded',String(!menu.hidden));});
 document.addEventListener('keydown',e=>{if(e.key==='Escape'&&!menu.hidden)close(true);});
 document.addEventListener('click',e=>{if(!e.target.closest('.menu-wrap'))close(false);});
 document.addEventListener('focusin',e=>{if(!e.target.closest('.menu-wrap'))close(false);});
})();
