// ===== STATE =====
let users = JSON.parse(localStorage.getItem('mb_users') || '[]');
let products = JSON.parse(localStorage.getItem('mb_products') || JSON.stringify([
  { id:'p1', vendorId:'demo-vendor', name:'Creamy Basil Pasta', category:'vegetarian', desc:'Al dente spaghetti tossed in a rich parmesan cream with fresh basil and toasted breadcrumbs.', price:7.99, time:25, cal:620, img:'https://images.unsplash.com/photo-1621996346565-e3dbc646d9a9?w=600&q=80' },
  { id:'p2', vendorId:'demo-vendor', name:'Herb-Crusted Salmon', category:'high protein', desc:'Pan-seared Atlantic salmon with roasted heritage vegetables and a lemon-herb glaze.', price:11.99, time:30, cal:480, img:'https://images.unsplash.com/photo-1467003909585-2f8a72700288?w=600&q=80' },
  { id:'p3', vendorId:'demo-vendor', name:'Thai Coconut Curry', category:'dairy-free', desc:'Fragrant green curry with tender vegetables, jasmine rice, and fresh cilantro-lime garnish.', price:9.49, time:35, cal:550, img:'https://images.unsplash.com/photo-1455619452474-d2be8b1e70cd?w=600&q=80' },
  { id:'p4', vendorId:'demo-vendor', name:'Lemon Garlic Chicken', category:'high protein', desc:'Juicy chicken thighs marinated with lemon, garlic, and fresh thyme served over roasted potatoes.', price:10.49, time:40, cal:520, img:'https://images.unsplash.com/photo-1598515214211-89d3c73ae83b?w=600&q=80' },
  { id:'p5', vendorId:'demo-vendor', name:'Mushroom Risotto', category:'vegetarian', desc:'Creamy arborio rice with wild mushrooms, parmesan, and fresh thyme. A comfort classic.', price:8.99, time:35, cal:590, img:'https://images.unsplash.com/photo-1476124369491-e7addf5db371?w=600&q=80' },
  { id:'p6', vendorId:'demo-vendor', name:'Vegan Buddha Bowl', category:'vegan', desc:'Roasted sweet potato, quinoa, chickpeas, avocado, and tahini dressing.', price:8.49, time:20, cal:420, img:'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=600&q=80' },
]));
let cart = [];
let orders = JSON.parse(localStorage.getItem('mb_orders') || '[]');
let currentUser = null;

function saveData() {
  localStorage.setItem('mb_users', JSON.stringify(users));
  localStorage.setItem('mb_products', JSON.stringify(products));
  localStorage.setItem('mb_orders', JSON.stringify(orders));
}

// ===== PAGE ROUTING =====
function showPage(id) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  window.scrollTo(0,0);
}

function scrollToSection(id) {
  document.getElementById(id)?.scrollIntoView({ behavior:'smooth' });
}

// ===== AUTH =====
function handleSignup() {
  const name = document.getElementById('signup-name').value.trim();
  const email = document.getElementById('signup-email').value.trim();
  const password = document.getElementById('signup-password').value;
  const role = document.querySelector('input[name="signup-role"]:checked').value;
  if (!name || !email || !password) return showToast('Please fill all fields','error');
  if (password.length < 6) return showToast('Password must be 6+ characters','error');
  if (users.find(u => u.email === email)) return showToast('Email already registered','error');
  const user = { id:'u'+Date.now(), name, email, password, role };
  users.push(user);
  saveData();
  currentUser = user;
  showToast('Account created! Welcome 🎉','success');
  goToDashboard(user);
}

function handleSignin() {
  const email = document.getElementById('signin-email').value.trim();
  const password = document.getElementById('signin-password').value;
  const user = users.find(u => u.email === email && u.password === password);
  // demo accounts
  if (!user) {
    if (email === 'customer@demo.com' && password === 'demo123') {
      currentUser = { id:'demo-customer', name:'Demo Customer', email, role:'customer' };
      showToast('Welcome back!','success');
      return goToDashboard(currentUser);
    }
    if (email === 'vendor@demo.com' && password === 'demo123') {
      currentUser = { id:'demo-vendor', name:'Demo Vendor Kitchen', email, role:'vendor' };
      showToast('Welcome back!','success');
      return goToDashboard(currentUser);
    }
    return showToast('Invalid email or password','error');
  }
  currentUser = user;
  showToast('Welcome back!','success');
  goToDashboard(user);
}

function goToDashboard(user) {
  if (user.role === 'customer') {
    document.getElementById('c-sidebar-name').textContent = user.name;
    document.getElementById('c-profile-name').value = user.name;
    document.getElementById('c-profile-email').value = user.email;
    renderCustomerProducts();
    renderOrders();
    showPage('customer-dashboard');
    showDashPanel('c-browse', null);
  } else {
    document.getElementById('v-sidebar-name').textContent = user.name;
    document.getElementById('v-profile-name').value = user.name;
    document.getElementById('v-profile-email').value = user.email;
    renderVendorTable();
    updateVendorStats();
    showPage('vendor-dashboard');
    showDashPanel('v-overview', null);
  }
}

function handleLogout() {
  currentUser = null;
  cart = [];
  updateCartUI();
  showPage('home');
  showToast('Signed out','success');
}

// ===== DASHBOARD PANELS =====
function showDashPanel(panelId, anchor) {
  const page = document.getElementById(panelId).closest('.page');
  page.querySelectorAll('.dash-panel').forEach(p => p.classList.remove('active'));
  document.getElementById(panelId).classList.add('active');
  if (anchor) {
    page.querySelectorAll('.sidebar-nav a').forEach(a => a.classList.remove('active'));
    if (typeof anchor === 'object') anchor.classList.add('active');
  }
  // sync sidebar
  page.querySelectorAll('.sidebar-nav a').forEach(a => {
    if (a.getAttribute('onclick') && a.getAttribute('onclick').includes(panelId)) a.classList.add('active');
    else a.classList.remove('active');
  });
}

// ===== PRODUCTS =====
function getVendorProducts() {
  if (!currentUser) return products;
  return products.filter(p => p.vendorId === currentUser.id);
}

function renderCustomerProducts(list) {
  const grid = document.getElementById('customer-products-grid');
  const items = list || products;
  if (!items.length) {
    grid.innerHTML = `<div class="empty-state" style="grid-column:1/-1"><i class="fa-solid fa-plate-wheat"></i><p>No meals found</p></div>`;
    return;
  }
  grid.innerHTML = items.map(p => `
    <div class="product-card">
      <img src="${p.img || 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=600&q=80'}" alt="${p.name}" onerror="this.src='https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=600&q=80'">
      <div class="product-body">
        <span class="meal-badge"><i class="fa-solid fa-leaf"></i>${p.category}</span>
        <h3>${p.name}</h3>
        <p class="desc">${p.desc}</p>
        <div class="product-meta">
          <span class="product-price">$${parseFloat(p.price).toFixed(2)}</span>
          <span class="product-time"><i class="fa-solid fa-clock"></i> ${p.time} min ${p.cal ? '· '+p.cal+' cal' : ''}</span>
        </div>
        <button class="btn-add" onclick="addToCart('${p.id}')"><i class="fa-solid fa-plus"></i> Add to Cart</button>
      </div>
    </div>
  `).join('');
}

function filterProducts() {
  const q = document.getElementById('customer-search').value.toLowerCase();
  const cat = document.getElementById('customer-filter').value.toLowerCase();
  const filtered = products.filter(p => {
    const matchQ = !q || p.name.toLowerCase().includes(q) || p.desc.toLowerCase().includes(q) || p.category.toLowerCase().includes(q);
    const matchCat = !cat || p.category.toLowerCase().includes(cat);
    return matchQ && matchCat;
  });
  renderCustomerProducts(filtered);
}

// Vendor products table
function renderVendorTable() {
  const q = (document.getElementById('vendor-search')?.value || '').toLowerCase();
  const vp = getVendorProducts().filter(p => !q || p.name.toLowerCase().includes(q));
  const tbody = document.getElementById('v-products-table');
  const tbodyOv = document.getElementById('v-overview-table');

  const rows = vp.length ? vp.map(p => `
    <tr>
      <td><img class="tbl-img" src="${p.img || 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=200&q=60'}" onerror="this.src='https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=200&q=60'"></td>
      <td><strong>${p.name}</strong></td>
      <td><span class="badge badge-orange">${p.category}</span></td>
      <td><strong>$${parseFloat(p.price).toFixed(2)}</strong></td>
      <td>${p.time} min</td>
      <td>
        <button class="btn-edit" onclick="editProduct('${p.id}')"><i class="fa-solid fa-pen"></i> Edit</button>
        <button class="btn-delete" onclick="deleteProduct('${p.id}')"><i class="fa-solid fa-trash"></i></button>
      </td>
    </tr>
  `).join('') : `<tr><td colspan="6" style="text-align:center;color:var(--gray);padding:2rem">No products yet. Add your first meal kit!</td></tr>`;

  if (tbody) tbody.innerHTML = rows;
  if (tbodyOv) tbodyOv.innerHTML = vp.length ? vp.slice(0,5).map(p => `
    <tr>
      <td><strong>${p.name}</strong></td>
      <td><span class="badge badge-orange">${p.category}</span></td>
      <td>$${parseFloat(p.price).toFixed(2)}</td>
      <td><span class="badge badge-green">Active</span></td>
      <td>
        <button class="btn-edit" onclick="editProduct('${p.id}');showDashPanel('v-add-product',null)"><i class="fa-solid fa-pen"></i> Edit</button>
        <button class="btn-delete" onclick="deleteProduct('${p.id}')"><i class="fa-solid fa-trash"></i></button>
      </td>
    </tr>
  `).join('') : `<tr><td colspan="5" style="text-align:center;color:var(--gray);padding:2rem">No products yet</td></tr>`;
}

function updateVendorStats() {
  const vp = getVendorProducts();
  document.getElementById('v-stat-products').textContent = vp.length;
  const rev = orders.filter(o => vp.some(p => p.id === o.productId)).reduce((s,o) => s + o.total, 0);
  document.getElementById('v-stat-revenue').textContent = '$' + rev.toFixed(2);
  document.getElementById('v-stat-orders').textContent = orders.filter(o => vp.some(p => p.id === o.productId)).length;
}

function resetProductForm() {
  document.getElementById('p-name').value = '';
  document.getElementById('p-category').value = '';
  document.getElementById('p-desc').value = '';
  document.getElementById('p-price').value = '';
  document.getElementById('p-time').value = '';
  document.getElementById('p-cal').value = '';
  document.getElementById('p-img').value = '';
  document.getElementById('p-edit-id').value = '';
  document.getElementById('product-form-title').textContent = 'Add New Product';
}

function saveProduct() {
  const name = document.getElementById('p-name').value.trim();
  const category = document.getElementById('p-category').value;
  const desc = document.getElementById('p-desc').value.trim();
  const price = parseFloat(document.getElementById('p-price').value);
  const time = parseInt(document.getElementById('p-time').value);
  const cal = parseInt(document.getElementById('p-cal').value) || null;
  const img = document.getElementById('p-img').value.trim();
  const editId = document.getElementById('p-edit-id').value;
  if (!name || !category || !desc || !price || !time) return showToast('Please fill required fields','error');
  if (editId) {
    const idx = products.findIndex(p => p.id === editId);
    if (idx !== -1) products[idx] = { ...products[idx], name, category, desc, price, time, cal, img };
    showToast('Product updated!','success');
  } else {
    products.push({ id:'p'+Date.now(), vendorId: currentUser.id, name, category, desc, price, time, cal, img });
    showToast('Product added!','success');
  }
  saveData();
  renderVendorTable();
  updateVendorStats();
  showDashPanel('v-products', null);
}

function editProduct(id, name, categoryId, desc, price, cookTime, calories) {
  document.getElementById('p-edit-id').value = id;
  document.getElementById('p-name').value = name;
  document.getElementById('p-category').value = categoryId;
  document.getElementById('p-desc').value = desc;
  document.getElementById('p-price').value = price;
  document.getElementById('p-time').value = cookTime;
  document.getElementById('p-cal').value = calories || '';
  document.getElementById('product-form-title').textContent = 'Edit Product';
  // Switch to Add/Edit panel
  showDashPanel('v-add-product', null);
}

function deleteProduct(id) {
  if (!confirm('Delete this product?')) return;
  products = products.filter(p => p.id !== id);
  saveData();
  renderVendorTable();
  updateVendorStats();
  showToast('Product deleted','success');
}

// ===== CART =====
function addToCart(productId) {
  const product = products.find(p => p.id === productId);
  if (!product) return;
  const existing = cart.find(i => i.id === productId);
  if (existing) existing.qty++;
  else cart.push({ ...product, qty: 1 });
  updateCartUI();
  showToast(`${product.name} added to cart!`, 'success');
}

function updateCartUI() {
  const total = cart.reduce((s,i) => s + i.qty, 0);
  document.getElementById('cart-count').textContent = total;
  document.getElementById('cart-count-badge').textContent = total;

  const listEl = document.getElementById('cart-items-list');
  const totalSec = document.getElementById('cart-total-section');
  if (!cart.length) {
    listEl.innerHTML = `<div class="empty-state"><i class="fa-solid fa-cart-shopping"></i><p>Your cart is empty</p></div>`;
    totalSec.style.display = 'none';
    return;
  }
  totalSec.style.display = 'block';
  listEl.innerHTML = cart.map(i => `
    <div class="cart-item">
      <img src="${i.img || 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=120&q=60'}" onerror="this.src='https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=120&q=60'">
      <div class="cart-item-info">
        <h4>${i.name}</h4>
        <p>$${parseFloat(i.price).toFixed(2)} / serving</p>
        <div class="cart-item-qty">
          <button class="qty-btn" onclick="changeQty('${i.id}',-1)">−</button>
          <span>${i.qty}</span>
          <button class="qty-btn" onclick="changeQty('${i.id}',1)">+</button>
        </div>
      </div>
      <strong>$${(i.qty * i.price).toFixed(2)}</strong>
    </div>
  `).join('');
  const subtotal = cart.reduce((s,i) => s + i.qty * i.price, 0);
  document.getElementById('cart-subtotal').textContent = '$' + subtotal.toFixed(2);
  document.getElementById('cart-total').textContent = '$' + subtotal.toFixed(2);
}

function changeQty(id, delta) {
  const item = cart.find(i => i.id === id);
  if (!item) return;
  item.qty += delta;
  if (item.qty <= 0) cart = cart.filter(i => i.id !== id);
  updateCartUI();
}

function openCart() { document.getElementById('cart-overlay').classList.add('open'); }
function closeCart() { document.getElementById('cart-overlay').classList.remove('open'); }
function closeCartOnOverlay(e) { if (e.target === document.getElementById('cart-overlay')) closeCart(); }

function placeOrder() {
  if (!cart.length) return;
  const total = cart.reduce((s,i) => s + i.qty * i.price, 0);
  cart.forEach(item => {
    orders.push({
      id: 'o'+Date.now()+Math.random(),
      userId: currentUser?.id,
      productId: item.id,
      productName: item.name,
      productImg: item.img,
      qty: item.qty,
      total: item.qty * item.price,
      date: new Date().toLocaleDateString()
    });
  });
  cart = [];
  saveData();
  updateCartUI();
  closeCart();
  renderOrders();
  showToast('Order placed! 🎉','success');
  showDashPanel('c-orders', null);
}

// ===== ORDERS =====
function renderOrders() {
  const list = document.getElementById('orders-list');
  if (!list) return;
  const myOrders = orders.filter(o => o.userId === currentUser?.id);
  if (!myOrders.length) {
    list.innerHTML = `<div class="empty-state"><i class="fa-solid fa-bag-shopping"></i><p>No orders yet. Start browsing meals!</p></div>`;
    return;
  }
  list.innerHTML = myOrders.slice().reverse().map(o => `
    <div class="order-card">
      <img src="${o.productImg || 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=120&q=60'}" onerror="this.src='https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=120&q=60'">
      <div class="order-info">
        <h4>${o.productName}</h4>
        <p>Qty: ${o.qty} · ${o.date}</p>
      </div>
      <span class="order-total">$${parseFloat(o.total).toFixed(2)}</span>
    </div>
  `).join('');
}

// ===== TOAST =====
function showToast(msg, type='success') {
  const wrap = document.getElementById('toast-wrap');
  const t = document.createElement('div');
  t.className = `toast ${type}`;
  t.innerHTML = `<i class="fa-solid ${type==='success'?'fa-circle-check':'fa-circle-xmark'}"></i> ${msg}`;
  wrap.appendChild(t);
  setTimeout(() => t.remove(), 3000);
}

// ===== HOME MEALS GRID =====
function renderHomeMeals() {
  const grid = document.getElementById('home-meals-grid');
  const featured = products.slice(0,3);
  grid.innerHTML = featured.map(p => `
    <div class="meal-card">
      <img class="meal-img" src="${p.img || 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=600&q=80'}" alt="${p.name}" onerror="this.src='https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=600&q=80'">
      <div class="meal-body">
        <span class="meal-badge"><i class="fa-solid fa-leaf"></i>${p.category}</span>
        <h3>${p.name}</h3>
        <p>${p.desc}</p>
        <div class="meal-meta">
          <span><i class="fa-solid fa-clock"></i> ${p.time} min</span>
          ${p.cal ? `<span><i class="fa-solid fa-fire"></i> ${p.cal} cal</span>` : ''}
        </div>
      </div>
    </div>
  `).join('');
}

// ===== INIT =====
renderHomeMeals();