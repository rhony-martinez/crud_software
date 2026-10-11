<script>
	import { page } from '$app/state';
	import favicon from '#lib/assets/favicon.svg';

	/** @type {{children: import('svelte').Snippet}} */
	let { children } = $props();
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
	<meta name="theme-color" content="#101d35" />
	<title>Clínica | Gestión médica</title>
</svelte:head>

<div class="app-shell">
	<aside class="sidebar">
		<a class="brand" href="/" aria-label="Clínica, inicio">
			<span class="brand-mark" aria-hidden="true">+</span>
			<span class="brand-copy">
				<strong>Clínica</strong>
				<small>Gestión médica</small>
			</span>
		</a>

		<p class="nav-label">MENÚ PRINCIPAL</p>
		<nav aria-label="Navegación principal">
			<a class:active={page.url.pathname === '/'} href="/" aria-current={page.url.pathname === '/' ? 'page' : undefined}>
				<span class="nav-icon" aria-hidden="true">⌂</span>
				<span>Inicio</span>
			</a>
			<a class:active={page.url.pathname.startsWith('/medicos')} href="/medicos" aria-current={page.url.pathname.startsWith('/medicos') ? 'page' : undefined}>
				<span class="nav-icon" aria-hidden="true">✚</span>
				<span>Médicos</span>
			</a>
			<a class:active={page.url.pathname.startsWith('/citas')} href="/citas" aria-current={page.url.pathname.startsWith('/citas') ? 'page' : undefined}>
				<span class="nav-icon" aria-hidden="true">▦</span>
				<span>Citas</span>
			</a>
		</nav>

		<div class="sidebar-note">
			<span class="note-dot" aria-hidden="true"></span>
			<span>
				<strong>Atención organizada</strong>
				<small>Administra médicos y citas</small>
			</span>
		</div>
	</aside>

	<div class="main-area">
		<header class="topbar">
			<div>
				<p class="topbar-kicker">SISTEMA DE ADMINISTRACIÓN</p>
				<p class="topbar-title">Centro médico</p>
			</div>
			<div class="topbar-badge"><span aria-hidden="true">●</span> Panel de gestión</div>
		</header>
		<main id="contenido">
			{@render children()}
		</main>
		<footer class="app-footer">Clínica <span aria-hidden="true">·</span> Administración de médicos y citas</footer>
	</div>
</div>

<style>
	:global(*) {
		box-sizing: border-box;
	}

	:global(body) {
		margin: 0;
		background: #f4f7fb;
		color: #1b2940;
		font-family:
			Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
		font-size: 15px;
		-webkit-font-smoothing: antialiased;
	}

	:global(button),
	:global(input),
	:global(select),
	:global(textarea) {
		font: inherit;
	}

	:global(button:focus-visible),
	:global(a:focus-visible),
	:global(input:focus-visible),
	:global(select:focus-visible),
	:global(textarea:focus-visible) {
		outline: 3px solid #8db4ff;
		outline-offset: 2px;
	}

	.app-shell {
		display: grid;
		grid-template-columns: 248px minmax(0, 1fr);
		min-height: 100vh;
	}

	.sidebar {
		position: sticky;
		top: 0;
		display: flex;
		height: 100vh;
		flex-direction: column;
		padding: 29px 19px 22px;
		background: #101d35;
		color: #f4f7ff;
	}

	.brand {
		display: flex;
		align-items: center;
		gap: 12px;
		margin: 0 8px 47px;
		color: inherit;
		text-decoration: none;
	}

	.brand-mark {
		display: grid;
		width: 39px;
		height: 39px;
		place-items: center;
		border-radius: 12px;
		background: #60c7b0;
		color: #10273b;
		font-size: 30px;
		font-weight: 500;
		line-height: 1;
	}

	.brand-copy strong,
	.brand-copy small,
	.sidebar-note strong,
	.sidebar-note small {
		display: block;
	}

	.brand-copy strong {
		font-size: 17px;
		letter-spacing: -0.3px;
	}

	.brand-copy small {
		margin-top: 3px;
		color: #a8b4c8;
		font-size: 11px;
	}

	.nav-label {
		margin: 0 10px 13px;
		color: #8190a9;
		font-size: 10px;
		font-weight: 700;
		letter-spacing: 1.1px;
	}

	nav {
		display: grid;
		gap: 6px;
	}

	nav a {
		display: flex;
		align-items: center;
		gap: 12px;
		min-height: 45px;
		padding: 0 12px;
		border-radius: 9px;
		color: #b7c2d3;
		font-size: 13px;
		font-weight: 550;
		text-decoration: none;
		transition: background 140ms ease, color 140ms ease;
	}

	nav a:hover,
	nav a.active {
		background: #1d2d49;
		color: #fff;
	}

	nav a.active {
		box-shadow: inset 3px 0 #61c8b1;
	}

	.nav-icon {
		width: 18px;
		color: #8fa2bc;
		font-size: 17px;
		text-align: center;
	}

	nav a.active .nav-icon {
		color: #75d9c2;
	}

	.sidebar-note {
		display: flex;
		align-items: flex-start;
		gap: 10px;
		margin-top: auto;
		padding: 14px 10px;
		border-top: 1px solid #2a3850;
	}

	.note-dot {
		width: 8px;
		height: 8px;
		margin-top: 4px;
		border-radius: 50%;
		background: #62c9ae;
		box-shadow: 0 0 0 4px rgb(98 201 174 / 12%);
	}

	.sidebar-note strong {
		font-size: 11px;
		font-weight: 600;
	}

	.sidebar-note small {
		margin-top: 4px;
		color: #9cabc1;
		font-size: 10px;
	}

	.main-area {
		display: flex;
		min-width: 0;
		min-height: 100vh;
		flex-direction: column;
	}

	.topbar {
		display: flex;
		min-height: 77px;
		align-items: center;
		justify-content: space-between;
		padding: 13px clamp(22px, 4vw, 54px);
		border-bottom: 1px solid #e7ecf3;
		background: #fff;
	}

	.topbar-kicker {
		margin: 0 0 3px;
		color: #8995a7;
		font-size: 9px;
		font-weight: 700;
		letter-spacing: 1.05px;
	}

	.topbar-title {
		margin: 0;
		color: #24334a;
		font-size: 13px;
		font-weight: 650;
	}

	.topbar-badge {
		display: flex;
		align-items: center;
		gap: 8px;
		padding: 8px 12px;
		border: 1px solid #e7edf3;
		border-radius: 20px;
		color: #637188;
		font-size: 11px;
	}

	.topbar-badge span {
		color: #5abca4;
		font-size: 9px;
	}

	main {
		width: 100%;
		max-width: 1440px;
		flex: 1;
		margin: 0 auto;
		padding: 39px clamp(22px, 4vw, 54px) 32px;
	}

	.app-footer {
		padding: 15px clamp(22px, 4vw, 54px);
		border-top: 1px solid #e7ecf3;
		color: #8995a7;
		font-size: 10px;
	}

	.app-footer span {
		padding: 0 4px;
		color: #60bda7;
	}

	@media (max-width: 760px) {
		.app-shell {
			grid-template-columns: 1fr;
		}

		.sidebar {
			position: static;
			height: auto;
			padding: 15px 18px 12px;
		}

		.brand {
			margin: 0 3px 15px;
		}

		.nav-label,
		.sidebar-note {
			display: none;
		}

		nav {
			grid-template-columns: repeat(3, 1fr);
		}

		nav a {
			justify-content: center;
			gap: 7px;
			min-height: 40px;
			padding: 0 5px;
			font-size: 12px;
		}

		nav a.active {
			box-shadow: inset 0 -3px #61c8b1;
		}

		.topbar {
			min-height: 61px;
		}

		main {
			padding-top: 28px;
		}
	}

	@media (max-width: 420px) {
		.topbar-badge {
			padding: 7px 9px;
			font-size: 10px;
		}
	}
</style>
