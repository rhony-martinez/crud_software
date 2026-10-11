<script>
	import { onMount } from 'svelte';
	import {
		actualizarMedico,
		crearMedico,
		eliminarMedico,
		listarMedicos,
		mensajeDeConexion
	} from '#lib/api.js';

	/** @typedef {import('#lib/api.js').Medico} Medico */
	/** @typedef {import('#lib/api.js').MedicoInput & {id?: number}} MedicoFormulario */

	const formularioVacio = () => ({ nombre: '', especialidad: '', correo: '' });

	let medicos = $state(/** @type {Medico[]} */ ([]));
	let formulario = $state(/** @type {MedicoFormulario} */ (formularioVacio()));
	let formularioAbierto = $state(false);
	let cargando = $state(true);
	let guardando = $state(false);
	let eliminandoId = $state(/** @type {number | null} */ (null));
	let errorCarga = $state('');
	let errorAccion = $state('');
	let exito = $state('');

	const editando = $derived(formulario.id !== undefined);

	async function cargarMedicos() {
		cargando = true;
		errorCarga = '';
		try {
			const resultado = await listarMedicos();
			if (!Array.isArray(resultado)) {
				throw new Error('La API no devolvió una lista de médicos válida.');
			}
			medicos = resultado;
		} catch (error) {
			errorCarga = mensajeDeConexion(error);
		} finally {
			cargando = false;
		}
	}

	function abrirNuevo() {
		formulario = formularioVacio();
		formularioAbierto = true;
		errorAccion = '';
		exito = '';
	}

	/** @param {Medico} medico */
	function abrirEdicion(medico) {
		formulario = {
			id: medico.id,
			nombre: medico.nombre,
			especialidad: medico.especialidad,
			correo: medico.correo
		};
		formularioAbierto = true;
		errorAccion = '';
		exito = '';
	}

	function cancelarEdicion() {
		formularioAbierto = false;
		formulario = formularioVacio();
		errorAccion = '';
	}

	/** @param {SubmitEvent} event */
	async function guardarMedico(event) {
		event.preventDefault();
		guardando = true;
		errorAccion = '';
		exito = '';
		const datos = {
			nombre: formulario.nombre.trim(),
			especialidad: formulario.especialidad.trim(),
			correo: formulario.correo.trim()
		};

		try {
			if (formulario.id !== undefined) {
				await actualizarMedico(formulario.id, datos);
				exito = 'Los datos del médico se actualizaron correctamente.';
			} else {
				await crearMedico(datos);
				exito = 'El médico se registró correctamente.';
			}
			formularioAbierto = false;
			formulario = formularioVacio();
			await cargarMedicos();
		} catch (error) {
			errorAccion = mensajeDeConexion(error);
		} finally {
			guardando = false;
		}
	}

	/** @param {Medico} medico */
	async function borrarMedico(medico) {
		if (!confirm(`¿Deseas eliminar a ${medico.nombre}?`)) {
			return;
		}

		eliminandoId = medico.id;
		errorAccion = '';
		exito = '';
		try {
			await eliminarMedico(medico.id);
			exito = 'El médico se eliminó correctamente.';
			await cargarMedicos();
		} catch (error) {
			errorAccion = mensajeDeConexion(error);
		} finally {
			eliminandoId = null;
		}
	}

	onMount(cargarMedicos);
</script>

<svelte:head>
	<title>Médicos | Clínica</title>
	<meta name="description" content="Consulta y administra el directorio de médicos de la clínica." />
</svelte:head>

<section class="page">
	<header class="page-heading">
		<div>
			<p class="eyebrow">DIRECTORIO</p>
			<h1>Médicos</h1>
			<p class="description">Administra los profesionales que atienden en la clínica.</p>
		</div>
		<button class="button button-primary" type="button" onclick={abrirNuevo}>
			<span class="plus" aria-hidden="true">+</span> Nuevo médico
		</button>
	</header>

	{#if errorAccion}
		<div class="alert alert-error" role="alert">
			<span class="alert-icon" aria-hidden="true">!</span>
			<p>{errorAccion}</p>
			<button class="alert-close" type="button" aria-label="Cerrar mensaje" onclick={() => (errorAccion = '')}>×</button>
		</div>
	{/if}
	{#if exito}
		<div class="alert alert-success" role="status">
			<span class="alert-icon" aria-hidden="true">✓</span>
			<p>{exito}</p>
			<button class="alert-close" type="button" aria-label="Cerrar mensaje" onclick={() => (exito = '')}>×</button>
		</div>
	{/if}

	{#if formularioAbierto}
		<section class="form-card panel" aria-labelledby="form-title">
			<div class="form-heading">
				<div>
					<p class="eyebrow">{editando ? 'ACTUALIZACIÓN' : 'NUEVO REGISTRO'}</p>
					<h2 id="form-title">{editando ? 'Editar médico' : 'Registrar médico'}</h2>
				</div>
				<button class="icon-button" type="button" aria-label="Cerrar formulario" onclick={cancelarEdicion}>×</button>
			</div>

			<form onsubmit={guardarMedico}>
				<div class="field-grid">
					<label class="field">
						<span>Nombre completo <span class="required">*</span></span>
						<input
							bind:value={formulario.nombre}
							class="input"
							name="nombre"
							type="text"
							placeholder="Ej. Laura Gómez"
							minlength="2"
							maxlength="100"
							autocomplete="name"
							required
						/>
					</label>
					<label class="field">
						<span>Especialidad <span class="required">*</span></span>
						<input
							bind:value={formulario.especialidad}
							class="input"
							name="especialidad"
							type="text"
							placeholder="Ej. Medicina general"
							minlength="2"
							maxlength="100"
							required
						/>
					</label>
					<label class="field field-full">
						<span>Correo electrónico <span class="required">*</span></span>
						<input
							bind:value={formulario.correo}
							class="input"
							name="correo"
							type="email"
							placeholder="nombre@clinica.test"
							maxlength="254"
							autocomplete="email"
							required
						/>
					</label>
				</div>
				<p class="form-hint"><span class="required">*</span> Campos obligatorios · El correo debe ser único.</p>
				<div class="form-actions">
					<button class="button button-secondary" type="button" onclick={cancelarEdicion}>Cancelar</button>
					<button class="button button-primary" type="submit" disabled={guardando}>
						{guardando ? 'Guardando…' : editando ? 'Guardar cambios' : 'Registrar médico'}
					</button>
				</div>
			</form>
		</section>
	{/if}

	<section class="list-card panel" aria-labelledby="list-title">
		<div class="list-heading">
			<div>
				<h2 id="list-title">Directorio médico</h2>
				<p>Profesionales registrados en el sistema</p>
			</div>
			<div class="list-tools">
				<span class="record-count">{medicos.length} {medicos.length === 1 ? 'médico' : 'médicos'}</span>
				<button class="refresh-button" type="button" onclick={cargarMedicos} disabled={cargando}>
					<span aria-hidden="true">↻</span> Actualizar
				</button>
			</div>
		</div>

		{#if errorCarga}
			<div class="load-error" role="alert">
				<strong>No se pudo cargar el directorio.</strong>
				<span>{errorCarga}</span>
				<button class="button button-secondary" type="button" onclick={cargarMedicos}>Reintentar</button>
			</div>
		{:else if cargando}
			<div class="loading-state" role="status">
				<span class="spinner" aria-hidden="true"></span> Cargando médicos…
			</div>
		{:else if medicos.length === 0}
			<div class="empty-state">
				<span class="empty-icon" aria-hidden="true">✚</span>
				<strong>Aún no hay médicos registrados</strong>
				<p>Agrega el primer profesional para comenzar a organizar las citas.</p>
				<button class="button button-primary" type="button" onclick={abrirNuevo}>Registrar médico</button>
			</div>
		{:else}
			<div class="table-scroll">
				<table>
					<thead>
						<tr>
							<th scope="col">MÉDICO</th>
							<th scope="col">ESPECIALIDAD</th>
							<th scope="col">CORREO ELECTRÓNICO</th>
							<th scope="col" class="actions-heading">ACCIONES</th>
						</tr>
					</thead>
					<tbody>
						{#each medicos as medico (medico.id)}
							<tr>
								<td data-label="Médico">
									<div class="doctor-cell">
										<span class="avatar" aria-hidden="true">{medico.nombre?.trim()?.charAt(0)?.toUpperCase() ?? 'M'}</span>
										<span>
											<strong>{medico.nombre}</strong>
											<small>ID #{medico.id}</small>
										</span>
									</div>
								</td>
								<td data-label="Especialidad"><span class="specialty">{medico.especialidad}</span></td>
								<td data-label="Correo electrónico"><a class="email" href={`mailto:${medico.correo}`}>{medico.correo}</a></td>
								<td data-label="Acciones">
									<div class="row-actions">
										<button class="action-button" type="button" onclick={() => abrirEdicion(medico)}>Editar</button>
										<button
											class="action-button delete-action"
											type="button"
											onclick={() => borrarMedico(medico)}
											disabled={eliminandoId === medico.id}
										>
											{eliminandoId === medico.id ? 'Eliminando…' : 'Eliminar'}
										</button>
									</div>
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		{/if}
	</section>
</section>

<style>
	.page {
		max-width: 1120px;
		margin: 0 auto;
	}

	.page-heading {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 20px;
		margin-bottom: 24px;
	}

	.eyebrow {
		margin: 0 0 7px;
		color: #4e9b87;
		font-size: 10px;
		font-weight: 750;
		letter-spacing: 1.1px;
	}

	h1 {
		margin: 0;
		color: #1e2e45;
		font-size: 29px;
		font-weight: 700;
		letter-spacing: -0.8px;
	}

	.description {
		margin: 8px 0 0;
		color: #7c899a;
		font-size: 12px;
	}

	.button {
		display: inline-flex;
		min-height: 39px;
		align-items: center;
		justify-content: center;
		gap: 8px;
		padding: 0 15px;
		border: 1px solid transparent;
		border-radius: 7px;
		cursor: pointer;
		font-size: 11px;
		font-weight: 650;
		transition: background 140ms ease, transform 140ms ease;
	}

	.button:hover:not(:disabled) {
		transform: translateY(-1px);
	}

	.button:disabled {
		cursor: wait;
		opacity: 0.65;
	}

	.button-primary {
		background: #258d79;
		color: white;
	}

	.button-primary:hover:not(:disabled) {
		background: #1d7867;
	}

	.button-secondary {
		border-color: #dce4ed;
		background: white;
		color: #53647b;
	}

	.button-secondary:hover:not(:disabled) {
		background: #f7fafc;
	}

	.plus {
		font-size: 18px;
		font-weight: 400;
		line-height: 1;
	}

	.panel {
		border: 1px solid #e7edf3;
		border-radius: 11px;
		background: white;
		box-shadow: 0 3px 12px rgb(30 52 80 / 3%);
	}

	.alert {
		display: flex;
		align-items: center;
		gap: 10px;
		margin-bottom: 13px;
		padding: 11px 13px;
		border: 1px solid;
		border-radius: 8px;
	}

	.alert p {
		flex: 1;
		margin: 0;
		font-size: 11px;
		line-height: 1.5;
	}

	.alert-error {
		border-color: #f2d2d0;
		background: #fff7f6;
		color: #9f4845;
	}

	.alert-success {
		border-color: #c9e9df;
		background: #f3fbf8;
		color: #347b69;
	}

	.alert-icon {
		font-size: 13px;
		font-weight: 800;
	}

	.alert-close,
	.icon-button {
		border: 0;
		background: transparent;
		color: #8895a5;
		cursor: pointer;
		font-size: 19px;
		line-height: 1;
	}

	.form-card {
		margin-bottom: 17px;
		padding: 21px 23px 20px;
	}

	.form-heading {
		display: flex;
		align-items: flex-start;
		justify-content: space-between;
		margin-bottom: 20px;
	}

	.form-heading .eyebrow {
		margin-bottom: 5px;
	}

	.form-heading h2,
	.list-heading h2 {
		margin: 0;
		color: #26364c;
		font-size: 15px;
		font-weight: 680;
	}

	.field-grid {
		display: grid;
		grid-template-columns: repeat(2, minmax(0, 1fr));
		gap: 16px;
	}

	.field {
		display: grid;
		gap: 7px;
		color: #4e5c70;
		font-size: 11px;
		font-weight: 650;
	}

	.field-full {
		grid-column: 1 / -1;
	}

	.required {
		color: #d56360;
	}

	.input {
		width: 100%;
		min-height: 40px;
		padding: 0 11px;
		border: 1px solid #dce4ed;
		border-radius: 6px;
		background: #fff;
		color: #26364c;
		font-size: 12px;
		font-weight: 400;
	}

	.input::placeholder {
		color: #aab4c1;
	}

	.input:focus {
		border-color: #68b7a4;
		outline: 3px solid rgb(104 183 164 / 13%);
	}

	.form-hint {
		margin: 13px 0 0;
		color: #8793a2;
		font-size: 10px;
	}

	.form-actions {
		display: flex;
		justify-content: flex-end;
		gap: 9px;
		margin-top: 20px;
		padding-top: 15px;
		border-top: 1px solid #edf0f4;
	}

	.list-card {
		overflow: hidden;
	}

	.list-heading {
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 15px;
		padding: 20px 22px;
	}

	.list-heading h2 {
		font-size: 14px;
	}

	.list-heading p {
		margin: 5px 0 0;
		color: #8b96a5;
		font-size: 10px;
	}

	.list-tools {
		display: flex;
		align-items: center;
		gap: 14px;
	}

	.record-count {
		padding: 5px 9px;
		border-radius: 20px;
		background: #edf7f4;
		color: #388976;
		font-size: 10px;
		font-weight: 650;
		white-space: nowrap;
	}

	.refresh-button {
		border: 0;
		background: transparent;
		color: #718096;
		cursor: pointer;
		font-size: 10px;
	}

	.refresh-button:disabled {
		cursor: wait;
		opacity: 0.5;
	}

	.refresh-button span {
		padding-right: 3px;
		font-size: 14px;
	}

	.table-scroll {
		overflow-x: auto;
		border-top: 1px solid #edf0f4;
	}

	table {
		width: 100%;
		border-collapse: collapse;
		text-align: left;
	}

	th {
		height: 39px;
		padding: 0 18px;
		background: #fafbfd;
		color: #8995a5;
		font-size: 9px;
		font-weight: 700;
		letter-spacing: 0.55px;
		white-space: nowrap;
	}

	td {
		padding: 13px 18px;
		border-top: 1px solid #f0f2f5;
		color: #57657a;
		font-size: 11px;
	}

	tbody tr:hover {
		background: #fcfdfd;
	}

	.actions-heading {
		text-align: right;
	}

	.doctor-cell {
		display: flex;
		align-items: center;
		gap: 10px;
	}

	.avatar {
		display: grid;
		width: 33px;
		height: 33px;
		flex: 0 0 auto;
		place-items: center;
		border-radius: 50%;
		background: #e9f4f1;
		color: #368c78;
		font-size: 12px;
		font-weight: 700;
	}

	.doctor-cell strong,
	.doctor-cell small {
		display: block;
	}

	.doctor-cell strong {
		color: #2c3a50;
		font-size: 11px;
		font-weight: 650;
	}

	.doctor-cell small {
		margin-top: 4px;
		color: #9aa4b1;
		font-size: 9px;
	}

	.specialty {
		display: inline-block;
		padding: 5px 8px;
		border-radius: 20px;
		background: #f0f4f8;
		color: #617188;
		font-size: 10px;
	}

	.email {
		color: #4d7185;
		text-decoration: none;
	}

	.email:hover {
		color: #267d6b;
		text-decoration: underline;
	}

	.row-actions {
		display: flex;
		justify-content: flex-end;
		gap: 6px;
	}

	.action-button {
		padding: 6px 8px;
		border: 1px solid #e1e7ee;
		border-radius: 5px;
		background: #fff;
		color: #52647a;
		cursor: pointer;
		font-size: 10px;
	}

	.action-button:hover:not(:disabled) {
		border-color: #b7c8d7;
		background: #f8fafc;
	}

	.delete-action {
		border-color: #f0dddd;
		color: #b45b58;
	}

	.delete-action:hover:not(:disabled) {
		border-color: #e9bfbd;
		background: #fff7f6;
	}

	.action-button:disabled {
		cursor: wait;
		opacity: 0.6;
	}

	.loading-state,
	.empty-state,
	.load-error {
		display: flex;
		align-items: center;
		justify-content: center;
		border-top: 1px solid #edf0f4;
		color: #7e8b9c;
		font-size: 11px;
	}

	.loading-state {
		min-height: 150px;
		gap: 10px;
	}

	.spinner {
		width: 16px;
		height: 16px;
		border: 2px solid #dbe9e5;
		border-top-color: #409982;
		border-radius: 50%;
		animation: spin 700ms linear infinite;
	}

	@keyframes spin {
		to {
			transform: rotate(360deg);
		}
	}

	.empty-state {
		min-height: 240px;
		flex-direction: column;
		padding: 27px 20px;
		text-align: center;
	}

	.empty-icon {
		display: grid;
		width: 43px;
		height: 43px;
		place-items: center;
		margin-bottom: 10px;
		border-radius: 13px;
		background: #edf7f4;
		color: #388976;
		font-size: 21px;
	}

	.empty-state strong {
		color: #39495e;
		font-size: 12px;
	}

	.empty-state p {
		margin: 7px 0 15px;
		color: #8a96a5;
		font-size: 10px;
	}

	.load-error {
		min-height: 170px;
		flex-direction: column;
		gap: 8px;
		padding: 23px;
		text-align: center;
	}

	.load-error strong {
		color: #a24f4b;
		font-size: 12px;
	}

	.load-error span {
		max-width: 470px;
		line-height: 1.5;
	}

	.load-error .button {
		margin-top: 4px;
	}

	@media (max-width: 700px) {
		.page-heading {
			align-items: flex-start;
		}

		.table-scroll {
			overflow: visible;
		}

		table,
		tbody,
		tr,
		td {
			display: block;
			width: 100%;
		}

		thead {
			display: none;
		}

		tbody {
			display: grid;
			gap: 0;
		}

		tbody tr {
			padding: 10px 16px;
			border-top: 1px solid #edf0f4;
		}

		td {
			display: grid;
			grid-template-columns: 116px minmax(0, 1fr);
			align-items: center;
			gap: 10px;
			padding: 7px 0;
			border: 0;
		}

		td::before {
			content: attr(data-label);
			color: #8995a5;
			font-size: 9px;
			font-weight: 700;
		}

		.row-actions {
			justify-content: flex-start;
		}

		.actions-heading {
			text-align: left;
		}
	}

	@media (max-width: 500px) {
		.page-heading {
			align-items: flex-start;
			flex-direction: column;
		}

		.page-heading > .button {
			width: 100%;
		}

		.field-grid {
			grid-template-columns: 1fr;
		}

		.field-full {
			grid-column: auto;
		}

		.form-card {
			padding: 18px 15px;
		}

		.list-heading {
			align-items: flex-start;
			padding: 17px 15px;
		}

		.list-tools {
			align-items: flex-end;
			flex-direction: column;
			gap: 7px;
		}

		td {
			grid-template-columns: 95px minmax(0, 1fr);
		}

		.email {
			overflow-wrap: anywhere;
		}
	}
</style>
