<script>
	import { onMount } from 'svelte';
	import { mensajeDeConexion, obtenerEstadoApi } from '#lib/api.js';

	let estado = $state('comprobando');
	let mensaje = $state('');

	async function comprobarConexion() {
		estado = 'comprobando';
		mensaje = '';

		try {
			const resultado = await obtenerEstadoApi();
			if (resultado?.estado !== 'ok') {
				throw new Error('La API respondió, pero su estado no es el esperado.');
			}
			estado = 'conectada';
		} catch (error) {
			estado = 'desconectada';
			mensaje = mensajeDeConexion(error);
		}
	}

	onMount(comprobarConexion);
</script>

<svelte:head>
	<meta
		name="description"
		content="Administra médicos y citas de la clínica desde un solo lugar."
	/>
</svelte:head>

<section class="page">
	<div class="welcome">
		<div class="welcome-copy">
			<p class="eyebrow">BIENVENIDO AL PANEL</p>
			<h1 class="page-title">Gestión de la clínica</h1>
			<p class="page-description">
				Administra la información de tus médicos y organiza las citas de tus pacientes.
			</p>
		</div>
		<div class="welcome-symbol" aria-hidden="true">+</div>
	</div>

	<section class="connection panel" aria-live="polite">
		<div class="connection-copy">
			<span class:online={estado === 'conectada'} class:offline={estado === 'desconectada'} class="connection-indicator" aria-hidden="true"></span>
			<div>
				<h2>Conexión con el backend</h2>
				<p>
					{#if estado === 'comprobando'}
						Comprobando la disponibilidad de la API…
					{:else if estado === 'conectada'}
						La API está disponible y lista para recibir solicitudes.
					{:else}
						{mensaje}
					{/if}
				</p>
			</div>
		</div>
		<div class="connection-actions">
			<span class:connected-text={estado === 'conectada'} class:disconnected-text={estado === 'desconectada'} class="connection-state">
				{estado === 'conectada' ? 'Conectada' : estado === 'desconectada' ? 'Sin conexión' : 'Verificando'}
			</span>
			<button class="button button-secondary" type="button" onclick={comprobarConexion} disabled={estado === 'comprobando'}>
				Volver a comprobar
			</button>
		</div>
	</section>

	<div class="section-heading">
		<div>
			<p class="eyebrow">ACCESOS DIRECTOS</p>
			<h2 class="section-title">¿Qué deseas administrar?</h2>
		</div>
	</div>

	<div class="shortcut-grid">
		<a class="shortcut-card panel" href="/medicos">
			<span class="shortcut-icon doctor-icon" aria-hidden="true">✚</span>
			<span class="shortcut-content">
				<strong>Médicos</strong>
				<span>Consulta y administra el directorio médico.</span>
				<span class="shortcut-link">Ir a médicos <span aria-hidden="true">→</span></span>
			</span>
		</a>
		<a class="shortcut-card panel" href="/citas">
			<span class="shortcut-icon appointment-icon" aria-hidden="true">▦</span>
			<span class="shortcut-content">
				<strong>Citas</strong>
				<span>Programa y consulta las citas de pacientes.</span>
				<span class="shortcut-link">Ir a citas <span aria-hidden="true">→</span></span>
			</span>
		</a>
	</div>

	<div class="info-note">
		<span aria-hidden="true">i</span>
		<p>Los cambios realizados se guardan en la base de datos de la clínica.</p>
	</div>
</section>

<style>
	.page {
		max-width: 1040px;
		margin: 0 auto;
	}

	.welcome {
		position: relative;
		display: flex;
		min-height: 193px;
		align-items: center;
		justify-content: space-between;
		overflow: hidden;
		padding: 34px 38px;
		border-radius: 15px;
		background: linear-gradient(110deg, #142844 0%, #1b3d5a 68%, #245c68 100%);
		color: white;
	}

	.welcome-copy {
		position: relative;
		z-index: 1;
		max-width: 560px;
	}

	.eyebrow {
		margin: 0 0 9px;
		color: #57a994;
		font-size: 10px;
		font-weight: 750;
		letter-spacing: 1.2px;
	}

	.welcome .eyebrow {
		color: #79d4bd;
	}

	.page-title {
		margin: 0;
		font-size: clamp(26px, 4vw, 35px);
		font-weight: 680;
		letter-spacing: -1.1px;
	}

	.page-description {
		max-width: 470px;
		margin: 12px 0 0;
		color: #c1d0dd;
		font-size: 13px;
		line-height: 1.7;
	}

	.welcome-symbol {
		display: grid;
		width: 103px;
		height: 103px;
		flex: 0 0 auto;
		place-items: center;
		margin-right: 20px;
		border: 1px solid rgb(255 255 255 / 22%);
		border-radius: 50%;
		background: rgb(255 255 255 / 7%);
		color: #7de0c3;
		font-size: 91px;
		font-weight: 200;
		line-height: 1;
	}

	.panel {
		border: 1px solid #e8edf3;
		border-radius: 12px;
		background: #fff;
		box-shadow: 0 3px 12px rgb(30 52 80 / 3%);
	}

	.connection {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 24px;
		margin-top: 22px;
		padding: 21px 23px;
	}

	.connection-copy {
		display: flex;
		align-items: flex-start;
		gap: 13px;
	}

	.connection-indicator {
		width: 9px;
		height: 9px;
		flex: 0 0 auto;
		margin-top: 5px;
		border-radius: 50%;
		background: #e5a54e;
		box-shadow: 0 0 0 4px #fff4e5;
	}

	.connection-indicator.online {
		background: #54b99f;
		box-shadow: 0 0 0 4px #e8f8f3;
	}

	.connection-indicator.offline {
		background: #df6c68;
		box-shadow: 0 0 0 4px #fff0ef;
	}

	.connection h2 {
		margin: 0;
		color: #24344b;
		font-size: 13px;
		font-weight: 650;
	}

	.connection p {
		margin: 6px 0 0;
		color: #7b8797;
		font-size: 11px;
		line-height: 1.5;
	}

	.connection-actions {
		display: flex;
		align-items: center;
		gap: 17px;
	}

	.connection-state {
		color: #b27c34;
		font-size: 11px;
		font-weight: 650;
		white-space: nowrap;
	}

	.connected-text {
		color: #398d78;
	}

	.disconnected-text {
		color: #bc5551;
	}

	.button {
		display: inline-flex;
		min-height: 37px;
		align-items: center;
		justify-content: center;
		gap: 8px;
		padding: 0 14px;
		border: 1px solid transparent;
		border-radius: 7px;
		cursor: pointer;
		font-size: 11px;
		font-weight: 650;
		text-decoration: none;
		transition: background 140ms ease, border-color 140ms ease, transform 140ms ease;
	}

	.button:hover:not(:disabled) {
		transform: translateY(-1px);
	}

	.button:disabled {
		cursor: wait;
		opacity: 0.65;
	}

	.button-secondary {
		border-color: #dce4ed;
		background: white;
		color: #52647d;
	}

	.button-secondary:hover:not(:disabled) {
		border-color: #b8c7d8;
		background: #f9fbfd;
	}

	.section-heading {
		display: flex;
		align-items: flex-end;
		justify-content: space-between;
		margin: 34px 0 16px;
	}

	.section-heading .eyebrow {
		margin-bottom: 6px;
	}

	.section-title {
		margin: 0;
		color: #203149;
		font-size: 17px;
		font-weight: 680;
		letter-spacing: -0.3px;
	}

	.shortcut-grid {
		display: grid;
		grid-template-columns: repeat(2, minmax(0, 1fr));
		gap: 15px;
	}

	.shortcut-card {
		display: flex;
		min-height: 150px;
		align-items: flex-start;
		gap: 15px;
		padding: 21px;
		color: inherit;
		text-decoration: none;
		transition: border-color 150ms ease, box-shadow 150ms ease, transform 150ms ease;
	}

	.shortcut-card:hover {
		transform: translateY(-2px);
		border-color: #cbd9e5;
		box-shadow: 0 8px 22px rgb(30 52 80 / 7%);
	}

	.shortcut-icon {
		display: grid;
		width: 41px;
		height: 41px;
		flex: 0 0 auto;
		place-items: center;
		border-radius: 11px;
		font-size: 20px;
	}

	.doctor-icon {
		background: #e9f5f2;
		color: #459c87;
	}

	.appointment-icon {
		background: #eff1ff;
		color: #6876c3;
	}

	.shortcut-content {
		display: grid;
		gap: 7px;
	}

	.shortcut-content > strong {
		color: #27374e;
		font-size: 14px;
	}

	.shortcut-content > span:not(.shortcut-link) {
		color: #7b8797;
		font-size: 11px;
		line-height: 1.5;
	}

	.shortcut-link {
		margin-top: 6px;
		color: #358f7a;
		font-size: 11px;
		font-weight: 650;
	}

	.info-note {
		display: flex;
		align-items: center;
		gap: 9px;
		margin-top: 22px;
		color: #7a8799;
	}

	.info-note > span {
		display: grid;
		width: 17px;
		height: 17px;
		place-items: center;
		border: 1px solid #b6c5d4;
		border-radius: 50%;
		color: #73859a;
		font-size: 10px;
		font-weight: 700;
	}

	.info-note p {
		margin: 0;
		font-size: 10px;
	}

	@media (max-width: 680px) {
		.welcome {
			min-height: 165px;
			padding: 27px 24px;
		}

		.welcome-symbol {
			width: 70px;
			height: 70px;
			margin-right: 0;
			font-size: 65px;
		}

		.connection {
			align-items: flex-start;
			flex-direction: column;
			gap: 17px;
		}

		.connection-actions {
			width: 100%;
			justify-content: space-between;
		}
	}

	@media (max-width: 520px) {
		.shortcut-grid {
			grid-template-columns: 1fr;
		}

		.welcome-symbol {
			display: none;
		}
	}
</style>
