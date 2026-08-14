-- Calixta | Catálogos administrables + flujo de pedidos
-- Ejecutar después de 20260731_tipos_producto.sql

-- ─────────────────────────────────────────────────────────────────────────────
-- Tipos de ingreso (contabilidad)
-- ─────────────────────────────────────────────────────────────────────────────
create table if not exists public.tipos_ingreso (
  id text primary key,
  nombre text not null unique,
  activo boolean not null default true,
  orden integer not null default 0,
  fecha_registro timestamptz not null default now()
);

create index if not exists idx_tipos_ingreso_activo
  on public.tipos_ingreso (activo, orden);

insert into public.tipos_ingreso (id, nombre, orden) values
  ('TIN-CAP', 'Capital', 10),
  ('TIN-INV', 'Inversión', 20),
  ('TIN-OTR', 'Otros ingresos', 30)
on conflict (id) do nothing;

-- ─────────────────────────────────────────────────────────────────────────────
-- Estados de pedido configurables
-- ─────────────────────────────────────────────────────────────────────────────
create table if not exists public.estados_pedido (
  id text primary key,
  nombre text not null unique,
  activo boolean not null default true,
  orden integer not null default 0,
  genera_venta boolean not null default false,
  revierte_venta boolean not null default false,
  es_inicial boolean not null default false,
  bloquea_edicion boolean not null default false,
  fecha_registro timestamptz not null default now(),
  constraint estados_pedido_flags_excluyentes check (not (genera_venta and revierte_venta))
);

create index if not exists idx_estados_pedido_activo
  on public.estados_pedido (activo, orden);

insert into public.estados_pedido (
  id, nombre, orden, genera_venta, revierte_venta, es_inicial, bloquea_edicion
) values
  ('EST-REC', 'Recibido', 10, false, false, true, false),
  ('EST-PAG', 'Pago Confirmado', 20, false, false, false, false),
  ('EST-ENV', 'Envío Agendado', 30, false, false, false, false),
  ('EST-ENT', 'Entregado', 40, true, false, false, true),
  ('EST-CAN', 'Cancelado', 50, false, true, false, true)
on conflict (id) do nothing;

-- ─────────────────────────────────────────────────────────────────────────────
-- Pedidos: estado dinámico + seguimiento reserva/venta
-- ─────────────────────────────────────────────────────────────────────────────
alter table public.pedidos
  add column if not exists venta_registrada boolean not null default false;

alter table public.pedidos
  add column if not exists stock_reservado boolean not null default false;

alter table public.pedidos alter column estado drop default;

alter table public.pedidos
  alter column estado type text using estado::text;

alter table public.pedidos
  alter column estado set default 'Recibido';

update public.pedidos
set venta_registrada = true
where estado = 'Entregado';

alter table public.pedidos
  drop constraint if exists pedidos_estado_fk;

alter table public.pedidos
  add constraint pedidos_estado_fk
  foreign key (estado) references public.estados_pedido (nombre) on delete restrict;

-- ─────────────────────────────────────────────────────────────────────────────
-- Contabilidad: quitar check fijo de categorías de ingreso
-- ─────────────────────────────────────────────────────────────────────────────
alter table public.contabilidad
  drop constraint if exists contabilidad_categoria_valida;

alter table public.contabilidad
  add constraint contabilidad_categoria_gasto_valida check (
    tipo <> 'Gasto'
    or categoria in ('Insumos', 'Equipos', 'Otros gastos')
  );

-- ─────────────────────────────────────────────────────────────────────────────
-- RLS
-- ─────────────────────────────────────────────────────────────────────────────
alter table public.tipos_ingreso enable row level security;
alter table public.estados_pedido enable row level security;

drop policy if exists "service_full_access_tipos_ingreso" on public.tipos_ingreso;
create policy "service_full_access_tipos_ingreso"
  on public.tipos_ingreso for all
  using (true) with check (true);

drop policy if exists "service_full_access_estados_pedido" on public.estados_pedido;
create policy "service_full_access_estados_pedido"
  on public.estados_pedido for all
  using (true) with check (true);
