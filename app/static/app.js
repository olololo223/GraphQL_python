// ================== СОСТОЯНИЕ ==================
const state = {
    token: localStorage.getItem("token") || null,
    role: localStorage.getItem("role") || null,
    booksOffset: 0,
    booksLimit: 10,
    booksTotal: 0,
};

// ================== GRAPHQL ==================
async function gql(query, variables = {}) {
    const headers = { "Content-Type": "application/json" };
    if (state.token) headers["Authorization"] = `Bearer ${state.token}`;
    const res = await fetch("/graphql", {
        method: "POST",
        headers,
        body: JSON.stringify({ query, variables }),
    });
    const data = await res.json();
    if (data.errors) {
        const msg = data.errors.map(e => e.message).join("; ");
        toast("❌ " + msg, "error");
        throw new Error(msg);
    }
    return data.data;
}

// ================== AUTH ==================
async function login() {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    const data = await gql(
        `mutation($e:String!,$p:String!){ login(email:$e,password:$p){ token role } }`,
        { e: email, p: password }
    );
    saveAuth(data.login.token, data.login.role);
}

async function register() {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    const data = await gql(
        `mutation($e:String!,$p:String!){ register(email:$e,password:$p){ token role } }`,
        { e: email, p: password }
    );
    saveAuth(data.register.token, data.register.role);
}

function saveAuth(token, role) {
    state.token = token;
    state.role = role;
    localStorage.setItem("token", token);
    localStorage.setItem("role", role);
    toast("✅ Вход выполнен (" + role + ")");
    renderAuth();
    loadAll();
}

function logout() {
    state.token = null;
    state.role = null;
    localStorage.removeItem("token");
    localStorage.removeItem("role");
    renderAuth();
}

function renderAuth() {
    const authPanel = document.getElementById("auth-panel");
    const userInfo = document.getElementById("user-info");
    const app = document.getElementById("app");
    if (state.token) {
        authPanel.style.display = "none";
        userInfo.style.display = "block";
        app.style.display = "block";
        document.getElementById("who").textContent =
            `${state.role === "admin" ? "👑" : "👤"} ${state.role}`;
        document.querySelectorAll(".admin-only").forEach(el => {
            el.style.display = state.role === "admin" ? "" : "none";
        });
    } else {
        authPanel.style.display = "block";
        userInfo.style.display = "none";
        app.style.display = "none";
    }
    applyRoleVisibility();
}

// ================== BOOKS ==================
async function loadBooks() {
    const filters = {
        search: document.getElementById("search").value || null,
        yearFrom: parseInt(document.getElementById("year-from").value) || null,
        yearTo: parseInt(document.getElementById("year-to").value) || null,
        minPrice: parseFloat(document.getElementById("min-price").value) || null,
        maxPrice: parseFloat(document.getElementById("max-price").value) || null,
        sortBy: document.getElementById("sort-by").value,
        limit: state.booksLimit,
        offset: state.booksOffset,
    };
    const data = await gql(
        `query($search:String,$yearFrom:Int,$yearTo:Int,$minPrice:Float,$maxPrice:Float,$sortBy:String!,$limit:Int!,$offset:Int!){
            books(search:$search,yearFrom:$yearFrom,yearTo:$yearTo,minPrice:$minPrice,maxPrice:$maxPrice,sortBy:$sortBy,limit:$limit,offset:$offset){
                total limit offset
                items { id title year price author { id name } }
            }
        }`,
        filters
    );
    const { items, total } = data.books;
    state.booksTotal = total;
    document.getElementById("books-total").textContent = `(всего: ${total})`;
    const tbody = document.querySelector("#books-table tbody");
    tbody.innerHTML = items.map(b => `
        <tr>
            <td>${b.id}</td>
            <td>${escapeHtml(b.title)}</td>
            <td>${b.year}</td>
            <td>${b.price.toFixed(2)} ₽</td>
            <td>${escapeHtml(b.author.name)}</td>
            <td class="admin-only">
                <button onclick="editBook(${b.id})">Изменить</button>
                <button onclick="deleteBook(${b.id})">Удалить</button>
            </td>
        </tr>
    `).join("");
    applyRoleVisibility();
    renderPagination();
}

function renderPagination() {
    const page = Math.floor(state.booksOffset / state.booksLimit) + 1;
    const totalPages = Math.max(1, Math.ceil(state.booksTotal / state.booksLimit));
    document.getElementById("page-info").textContent = `Стр. ${page} из ${totalPages}`;
}

function nextPage() {
    if (state.booksOffset + state.booksLimit < state.booksTotal) {
        state.booksOffset += state.booksLimit;
        loadBooks();
    }
}

function prevPage() {
    if (state.booksOffset > 0) {
        state.booksOffset -= state.booksLimit;
        loadBooks();
    }
}

// ================== AUTHORS ==================
async function loadAuthors() {
    const data = await gql(`{
        authors(limit: 100){ items { id name country } total }
    }`);
    const tbody = document.querySelector("#authors-table tbody");
    tbody.innerHTML = data.authors.items.map(a => `
        <tr>
            <td>${a.id}</td>
            <td>${escapeHtml(a.name)}</td>
            <td>${escapeHtml(a.country)}</td>
            <td class="admin-only">
                <button onclick="editAuthor(${a.id})">Изменить</button>
                <button onclick="deleteAuthor(${a.id})">Удалить</button>
            </td>
        </tr>
    `).join("");
    document.getElementById("authors-total").textContent = `(всего: ${data.authors.total})`;

    // Обновляем список авторов в модалке книги
    const select = document.getElementById("book-author");
    select.innerHTML = data.authors.items.map(a =>
        `<option value="${a.id}">${escapeHtml(a.name)}</option>`
    ).join("");

    applyRoleVisibility();
}

// ================== BOOK CRUD ==================
function openBookModal(book = null) {
    document.getElementById("book-modal-title").textContent = book ? "Редактировать книгу" : "Новая книга";
    document.getElementById("book-id").value = book?.id || "";
    document.getElementById("book-title").value = book?.title || "";
    document.getElementById("book-year").value = book?.year || new Date().getFullYear();
    document.getElementById("book-price").value = book?.price || 0;
    if (book) document.getElementById("book-author").value = book.author.id;
    document.getElementById("book-modal").style.display = "flex";
}

async function editBook(id) {
    const data = await gql(`query($id:Int!){ book(id:$id){ id title year price author { id } } }`, { id });
    openBookModal(data.book);
}

async function saveBook() {
    const id = document.getElementById("book-id").value;
    const input = {
        title: document.getElementById("book-title").value,
        year: parseInt(document.getElementById("book-year").value),
        price: parseFloat(document.getElementById("book-price").value),
        authorId: parseInt(document.getElementById("book-author").value),
    };
    if (id) {
        await gql(
            `mutation($id:Int!,$data:BookInput!){ updateBook(id:$id,data:$data){ id } }`,
            { id: parseInt(id), data: input }
        );
    } else {
        await gql(
            `mutation($data:BookInput!){ addBook(data:$data){ id } }`,
            { data: input }
        );
    }
    closeModal("book-modal");
    toast("✅ Сохранено");
    loadBooks();
}

async function deleteBook(id) {
    if (!confirm("Удалить книгу?")) return;
    await gql(`mutation($id:Int!){ deleteBook(id:$id) }`, { id });
    toast("🗑 Удалено");
    loadBooks();
}

// ================== AUTHOR CRUD ==================
function openAuthorModal(author = null) {
    document.getElementById("author-modal-title").textContent = author ? "Редактировать автора" : "Новый автор";
    document.getElementById("author-id").value = author?.id || "";
    document.getElementById("author-name").value = author?.name || "";
    document.getElementById("author-country").value = author?.country || "";
    document.getElementById("author-modal").style.display = "flex";
}

async function editAuthor(id) {
    const data = await gql(`query($id:Int!){ author(id:$id){ id name country } }`, { id });
    openAuthorModal(data.author);
}

async function saveAuthor() {
    const id = document.getElementById("author-id").value;
    const input = {
        name: document.getElementById("author-name").value,
        country: document.getElementById("author-country").value,
    };
    if (id) {
        await gql(
            `mutation($id:Int!,$data:AuthorInput!){ updateAuthor(id:$id,data:$data){ id } }`,
            { id: parseInt(id), data: input }
        );
    } else {
        await gql(
            `mutation($data:AuthorInput!){ addAuthor(data:$data){ id } }`,
            { data: input }
        );
    }
    closeModal("author-modal");
    toast("✅ Сохранено");
    loadAuthors();
    loadBooks();
}

async function deleteAuthor(id) {
    if (!confirm("Удалить автора? Все его книги тоже удалятся.")) return;
    await gql(`mutation($id:Int!){ deleteAuthor(id:$id) }`, { id });
    toast("🗑 Удалено");
    loadAuthors();
    loadBooks();
}

// ================== УТИЛИТЫ ==================
function closeModal(id) { document.getElementById(id).style.display = "none"; }
function escapeHtml(s) { return String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c])); }

function toast(msg, type = "ok") {
    const t = document.getElementById("toast");
    t.textContent = msg;
    t.className = type;
    t.style.opacity = "1";
    setTimeout(() => { t.style.opacity = "0"; }, 2500);
}

let debounceTimer;
function debouncedLoadBooks() {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => { state.booksOffset = 0; loadBooks(); }, 300);
}

function loadAll() { loadBooks(); loadAuthors(); }

// ================== СТАРТ ==================
renderAuth();
if (state.token) loadAll();

function applyRoleVisibility() {
    const isAdmin = state.role === "admin";
    document.querySelectorAll(".admin-only").forEach(el => {
        // Для <th>/<td> нужен table-cell, для остальных — inline-block
        const tag = el.tagName;
        const showValue = (tag === "TD" || tag === "TH") ? "table-cell" : "inline-block";
        el.style.display = isAdmin ? showValue : "none";
    });
}