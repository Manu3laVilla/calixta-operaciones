-- Calixta | Tipos de gasto administrables
-- Ejecutar después de 20260731_admin_catalogos.sql

create table if not exists public.tipos_gasto (
  id text primary key,
  nombre text not null unique,
  activo boolean not null default true,
  fecha_registro timestamptz not null default now()
);

create index if not exists idx_tipos_gasto_activo
  on public.tipos_gasto (activo, nombre);

insert into public.tipos_gasto (id, nombre) values
  ('TGA-INS', 'Insumos'),
  ('TGA-EQU', 'Equipos'),
  ('TGA-OTR', 'Otros gastos')
on conflict (id) do nothing;

alter table public.contabilidad
  drop constraint if exists contabilidad_categoria_gasto_valida;

alter table public.tipos_gasto enable row level security;

drop policy if exists "service_full_access_tipos_gasto" on public.tipos_gasto;

create policy "service_full_access_tipos_gasto"
  on public.tipos_gasto for all
  using (true) with check (true);
