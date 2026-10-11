<script>
  import { onMount } from 'svelte';

  const API = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';
  let estado = $state('comprobando...');

  onMount(async () => {
    try {
      const res = await fetch(`${API}/salud`);
      estado = (await res.json()).estado;
    } catch {
      estado = 'sin conexión con la API';
    }
  });
</script>

<h1>Clínica</h1>
<p>Estado de la API: {estado}</p>