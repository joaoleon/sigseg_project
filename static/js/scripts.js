document.addEventListener("DOMContentLoaded", function() {
    let token = localStorage.getItem("access_token");
    let navbarMenu = document.getElementById("navbarNav");

    // 🔹 Atualiza a navbar dinamicamente
    function atualizarNavbar() {
        if (token) {
            fetch("/auth/status", {
                method: "GET",
                headers: { "Authorization": "Bearer " + token }
            })
            .then(response => response.json())
            .then(data => {
                navbarMenu.innerHTML = "";  // Limpa a navbar antes de atualizar

                navbarMenu.innerHTML += `
                    <li class="nav-item"><a href="/" class="nav-link">Página Inicial</a></li>
                    <li class="nav-item"><a href="/faq" class="nav-link">Perguntas Frequentes</a></li>`;

                if (data.logged_in) {
                    navbarMenu.innerHTML += `
                        <li class="nav-item"><a href="/monitoramento" class="nav-link">Monitoramento</a></li>
                        <li class="nav-item"><a href="/cadastrar-objeto" class="nav-link">Cadastrar Objeto</a></li>
                        <li class="nav-item"><a href="/perfil" class="nav-link">Perfil</a></li>
                        <li class="nav-item">
                            <a href="#" class="nav-link text-danger fw-bold" onclick="logout()">
                                <i class="bi bi-box-arrow-right"></i> Sair
                            </a>
                        </li>`;
                } else {
                    navbarMenu.innerHTML += `
                        <li class="nav-item"><a href="/auth/login" class="nav-link">Login</a></li>
                        <li class="nav-item">
                            <a href="/auth/register" class="nav-link btn btn-warning text-dark fw-bold">
                                <i class="bi bi-person-plus-fill"></i> Cadastre-se
                            </a>
                        </li>`;
                }
            })
            .catch(error => console.error("Erro ao verificar autenticação:", error));
        } else {
            navbarMenu.innerHTML = `
                <li class="nav-item"><a href="/" class="nav-link">Página Inicial</a></li>
                <li class="nav-item"><a href="/faq" class="nav-link">Perguntas Frequentes</a></li>
                <li class="nav-item"><a href="/auth/login" class="nav-link">Login</a></li>
                <li class="nav-item">
                    <a href="/auth/register" class="nav-link btn btn-warning text-dark fw-bold">
                        <i class="bi bi-person-plus-fill"></i> Cadastre-se
                    </a>
                </li>`;
        }
    }

    atualizarNavbar(); // Atualiza a navbar ao carregar a página

    // 🔹 Função de Logout
    function logout() {
        fetch("/logout", { method: "POST" })
        .then(response => response.json())
        .then(data => {
            if (data.logout) {
                localStorage.removeItem("access_token");
                window.location.href = "/";
            }
        })
        .catch(error => console.error("Erro ao fazer logout:", error));
    }

    // 🔹 Gerenciamento de Objetos Roubados
    const form = document.getElementById("form-objeto");
    const listaObjetos = document.getElementById("lista-objetos");

    function carregarObjetos() {
        fetch("/objetos_roubados", {
            method: "GET",
            headers: { 
                "Content-Type": "application/json",
                "Authorization": "Bearer " + token  // 🔥 Inclui o token JWT
            }
        })
        .then(response => response.json())
        .then(data => {
            listaObjetos.innerHTML = "";
            data.forEach(objeto => {
                const item = document.createElement("li");
                item.textContent = `${objeto.nome_objeto} - ${objeto.tipo_objeto}`;
                listaObjetos.appendChild(item);
            });
        })
        .catch(error => console.error("Erro ao carregar objetos:", error));
    }

    // 🔹 Cadastro de Novo Objeto
    if (form) {
        form.addEventListener("submit", function(event) {
            event.preventDefault();

            const formData = {
                nome_objeto: document.getElementById("nome_objeto").value,
                tipo_objeto: document.getElementById("tipo_objeto").value
            };

            fetch("/objetos_roubados", {
                method: "POST",
                headers: { 
                    "Content-Type": "application/json",
                    "Authorization": "Bearer " + token  // 🔥 Inclui o token JWT
                },
                body: JSON.stringify(formData)
            })
            .then(response => response.json())
            .then(data => {
                console.log("Objeto cadastrado:", data);
                carregarObjetos();
                form.reset();
            })
            .catch(error => console.error("Erro ao cadastrar objeto:", error));
        });
    }

    // 🔹 Carregar lista de objetos ao iniciar
    if (listaObjetos) {
        carregarObjetos();
    }

    // 🔹 Filtro de Busca na Tabela
    function filterTable() {
        let input = document.getElementById("searchBar").value.toLowerCase();
        let rows = document.querySelectorAll("tbody tr");

        rows.forEach(row => {
            let nome = row.cells[1].textContent.toLowerCase();
            let tipo = row.cells[2].textContent.toLowerCase();
            row.style.display = (nome.includes(input) || tipo.includes(input)) ? "" : "none";
        });
    }

    // 🔹 Confirmação ao Excluir Objeto
    function confirmDelete() {
        return confirm("⚠️ Tem certeza que deseja excluir este objeto?");
    }
});

    // 🔹 Atualiza a navbar dinamicamente
    document.addEventListener("DOMContentLoaded", function() {
        let loginForm = document.getElementById("login-form");
    
        if (loginForm) {
            loginForm.addEventListener("submit", function(event) {
                event.preventDefault(); // 🔥 Impede o reload da página
    
                let formData = new FormData(this);
                let jsonData = JSON.stringify(Object.fromEntries(formData));
    
                fetch("/auth/login", {
                    method: "POST",
                    body: jsonData,
                    headers: { "Content-Type": "application/json" },
                    credentials: "include"  // 🔥 Garante que os cookies sejam enviados
                })
                .then(response => response.json())
                .then(data => {
                    console.log("Resposta da API:", data); // ✅ Debug para verificar a resposta
                    window.location.href = "/"; // Redireciona para a página inicial
                })
                .catch(error => console.error("Erro ao processar login:", error));
            });
        }
    });
    
