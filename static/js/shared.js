// ===== SHARED STATE & UTILITIES =====

const DEFAULT_PRODUCTS = [
  { id:'p1', vendorId:'demo-vendor', name:'Creamy Basil Pasta', category:'vegetarian', desc:'Al dente spaghetti tossed in a rich parmesan cream with fresh basil and toasted breadcrumbs.', price:7.99, time:25, cal:620, img:'https://images.unsplash.com/photo-1621996346565-e3dbc646d9a9?w=600&q=80' },
  { id:'p2', vendorId:'demo-vendor', name:'Herb-Crusted Salmon', category:'high protein', desc:'Pan-seared Atlantic salmon with roasted heritage vegetables and a lemon-herb glaze.', price:11.99, time:30, cal:480, img:'https://images.unsplash.com/photo-1467003909585-2f8a72700288?w=600&q=80' },
  { id:'p3', vendorId:'demo-vendor', name:'Thai Coconut Curry', category:'dairy-free', desc:'Fragrant green curry with tender vegetables, jasmine rice, and fresh cilantro-lime garnish.', price:9.49, time:35, cal:550, img:'https://images.unsplash.com/photo-1455619452474-d2be8b1e70cd?w=600&q=80' },
  { id:'p4', vendorId:'demo-vendor', name:'Lemon Garlic Chicken', category:'high protein', desc:'Juicy chicken thighs marinated with lemon, garlic, and fresh thyme served over roasted potatoes.', price:10.49, time:40, cal:520, img:'https://images.unsplash.com/photo-1598515214211-89d3c73ae83b?w=600&q=80' },
  { id:'p5', vendorId:'demo-vendor', name:'Mushroom Risotto', category:'vegetarian', desc:'Creamy arborio rice with wild mushrooms, parmesan, and fresh thyme. A comfort classic.', price:8.99, time:35, cal:590, img:'https://images.unsplash.com/photo-1476124369491-e7addf5db371?w=600&q=80' },
  { id:'p6', vendorId:'demo-vendor', name:'Vegan Buddha Bowl', category:'vegan', desc:'Roasted sweet potato, quinoa, chickpeas, avocado, and tahini dressing.', price:8.49, time:20, cal:420, img:'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=600&q=80' },
];

// ===== DATA ACCESS =====
function getUsers()    { return JSON.parse(localStorage.getItem('mb_users') || '[]'); }
function getProducts() { return JSON.parse(localStorage.getItem('mb_products') || JSON.stringify(DEFAULT_PRODUCTS)); }
function getOrders()   { return JSON.parse(localStorage.getItem('mb_orders') || '[]'); }
function getCurrentUser() { return JSON.parse(sessionStorage.getItem('mb_current_user') || 'null'); }

function saveUsers(users)       { localStorage.setItem('mb_users', JSON.stringify(users)); }
function saveProducts(products) { localStorage.setItem('mb_products', JSON.stringify(products)); }
function saveOrders(orders)     { localStorage.setItem('mb_orders', JSON.stringify(orders)); }
function saveCurrentUser(user)  { sessionStorage.setItem('mb_current_user', JSON.stringify(user)); }
function clearCurrentUser()     { sessionStorage.removeItem('mb_current_user'); }

// Ensure products always initialized
if (!localStorage.getItem('mb_products')) saveProducts(DEFAULT_PRODUCTS);

// ===== TOAST =====
function showToast(msg, type = 'success') {
  let wrap = document.getElementById('toast-wrap');
  if (!wrap) {
    wrap = document.createElement('div');
    wrap.id = 'toast-wrap';
    wrap.className = 'toast-wrap';
    document.body.appendChild(wrap);
  }
  const t = document.createElement('div');
  t.className = `toast ${type}`;
  t.innerHTML = `<i class="fa-solid ${type === 'success' ? 'fa-circle-check' : 'fa-circle-xmark'}"></i> ${msg}`;
  wrap.appendChild(t);
  setTimeout(() => t.remove(), 3000);
}

// ===== DASHBOARD PANELS =====
function showDashPanel(panelId) {
  document.querySelectorAll('.dash-panel').forEach(p => p.classList.remove('active'));
  const panel = document.getElementById(panelId);
  if (panel) panel.classList.add('active');

  document.querySelectorAll('.sidebar-nav li a').forEach(a => {
    a.classList.remove('active');
    const onclick = a.getAttribute('onclick') || '';
    if (onclick.includes(panelId)) a.classList.add('active');
  });
}

// ===== AUTH GUARD =====
function requireAuth(role = null) {
  const user = getCurrentUser();

  if (!user) {
    window.location.replace('/signin/');
    return null;
  }

  if (role && user.role !== role) {
    if (user.role === 'vendor') {
      window.location.replace('/vendor/dashboard/');
    } else {
      window.location.replace('/customer/dashboard/');
    }
    return null;
  }

  return user;
}