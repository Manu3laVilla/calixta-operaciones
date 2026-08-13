-- Calixta | Centro de Operaciones
-- Esquema PostgreSQL para Supabase
-- Ejecutar en: Supabase Dashboard → SQL Editor → New query

-- ─────────────────────────────────────────────────────────────────────────────
-- Extensiones
-- ─────────────────────────────────────────────────────────────────────────────
create extension if not exists "pgcrypto";

-- ─────────────────────────────────────────────────────────────────────────────
-- Tipos enumerados (alineados con config.py)
-- ─────────────────────────────────────────────────────────────────────────────
create type categoria_producto as enum ('Ropa', 'Accesorio');
create type talla_producto as enum ('XS', 'S', 'M', 'L', 'XL', 'Talla Única');
create type estado_pedido as enum (
  'Recibido',
  'Pago Confirmado',
  'Envío Agendado',
  'Entregado'
);
create type tipo_movimiento as enum ('Ingreso', 'Gasto');
create type categoria_ingreso as enum ('Capital', 'Inversión', 'Otros ingresos');
create type categoria_gasto as enum ('Insumos', 'Equipos', 'Otros gastos');

-- ─────────────────────────────────────────────────────────────────────────────
-- Productos
-- ─────────────────────────────────────────────────────────────────────────────
create table public.productos (
  id text primary key,
  referencia text not null,
  nombre text not null,
  color text not null default '',
  talla talla_producto not null,
  categoria categoria_producto not null,
  descripcion text not null default '',
  stock integer not null default 0 check (stock >= 0),
  stock_minimo integer not null default 0 check (stock_minimo >= 0),
  precio numeric(12, 2) not null default 0 check (precio >= 0),
  activo boolean not null default true,
  fecha_registro timestamptz not null default now()
);

create index idx_productos_referencia on public.productos (referencia);
create index idx_productos_activo on public.productos (activo);
create index idx_productos_stock_minimo on public.productos (stock_minimo);

-- ─────────────────────────────────────────────────────────────────────────────
-- Clientes
-- ─────────────────────────────────────────────────────────────────────────────
create table public.clientes (
  id text primary key,
  nombre text not null,
  email text not null default '',
  telefono text not null default '',
  direccion text not null default '',
  notas text not null default '',
  fecha_registro timestamptz not null default now()
);

create index idx_clientes_nombre on public.clientes (nombre);

-- ─────────────────────────────────────────────────────────────────────────────
-- Pedidos
-- ─────────────────────────────────────────────────────────────────────────────
create table public.pedidos (
  id text primary key,
  cliente_id text not null references public.clientes (id) on delete restrict,
  cliente_nombre text not null,
  total numeric(12, 2) not null default 0 check (total >= 0),
  estado estado_pedido not null default 'Recibido',
  direccion_entrega text not null,
  fecha_entrega timestamptz,
  fecha_creacion timestamptz not null default now(),
  fecha_actualizacion timestamptz not null default now(),
  notas text not null default ''
);

create index idx_pedidos_cliente on public.pedidos (cliente_id);
create index idx_pedidos_estado on public.pedidos (estado);
create index idx_pedidos_fecha_creacion on public.pedidos (fecha_creacion desc);

-- Ítems del pedido (reemplaza items_json de Google Sheets)
create table public.pedido_items (
  id bigserial primary key,
  pedido_id text not null references public.pedidos (id) on delete cascade,
  producto_id text not null references public.productos (id) on delete restrict,
  referencia text not null default '',
  producto_nombre text not null default '',
  color text not null default '',
  talla text not null default '',
  cantidad integer not null check (cantidad > 0),
  precio_unitario numeric(12, 2) not null check (precio_unitario >= 0),
  subtotal numeric(12, 2) not null check (subtotal >= 0)
);

create index idx_pedido_items_pedido on public.pedido_items (pedido_id);
create index idx_pedido_items_producto on public.pedido_items (producto_id);

-- ─────────────────────────────────────────────────────────────────────────────
-- Ventas (generadas al entregar pedidos)
-- ─────────────────────────────────────────────────────────────────────────────
create table public.ventas (
  id text primary key,
  fecha_entrega timestamptz not null,
  pedido_id text not null references public.pedidos (id) on delete restrict,
  cliente_id text not null references public.clientes (id) on delete restrict,
  cliente_nombre text not null,
  producto_id text not null references public.productos (id) on delete restrict,
  referencia text not null default '',
  producto_nombre text not null default '',
  color text not null default '',
  talla text not null default '',
  cantidad integer not null check (cantidad > 0),
  precio_unitario numeric(12, 2) not null check (precio_unitario >= 0),
  subtotal numeric(12, 2) not null check (subtotal >= 0)
);

create index idx_ventas_fecha on public.ventas (fecha_entrega desc);
create index idx_ventas_cliente on public.ventas (cliente_id);
create index idx_ventas_pedido on public.ventas (pedido_id);
create index idx_ventas_producto on public.ventas (producto_id);

-- ─────────────────────────────────────────────────────────────────────────────
-- Contabilidad
-- ─────────────────────────────────────────────────────────────────────────────
create table public.contabilidad (
  id text primary key,
  fecha date not null,
  tipo tipo_movimiento not null,
  categoria text not null,
  concepto text not null,
  monto numeric(12, 2) not null check (monto > 0),
  notas text not null default '',
  fecha_registro timestamptz not null default now(),
  fecha_actualizacion timestamptz not null default now(),
  constraint contabilidad_categoria_valida check (
    (tipo = 'Ingreso' and categoria in ('Capital', 'Inversión', 'Otros ingresos'))
    or (tipo = 'Gasto' and categoria in ('Insumos', 'Equipos', 'Otros gastos'))
  )
);

create index idx_contabilidad_fecha on public.contabilidad (fecha desc);
create index idx_contabilidad_tipo on public.contabilidad (tipo);

-- ─────────────────────────────────────────────────────────────────────────────
-- Trigger: actualizar fecha_actualizacion en pedidos y contabilidad
-- ─────────────────────────────────────────────────────────────────────────────
create or replace function public.set_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.fecha_actualizacion = now();
  return new;
end;
$$;

create trigger trg_pedidos_updated_at
before update on public.pedidos
for each row
execute function public.set_updated_at();

create trigger trg_contabilidad_updated_at
before update on public.contabilidad
for each row
execute function public.set_updated_at();

-- ─────────────────────────────────────────────────────────────────────────────
-- Seguridad (RLS)
-- App interna: acceso solo con service_role desde el backend (Python).
-- ─────────────────────────────────────────────────────────────────────────────
alter table public.productos enable row level security;
alter table public.clientes enable row level security;
alter table public.pedidos enable row level security;
alter table public.pedido_items enable row level security;
alter table public.ventas enable row level security;
alter table public.contabilidad enable row level security;

-- Políticas permisivas para el rol autenticado de servicio (service_role bypass RLS).
-- Si más adelante usas auth de Supabase, restringe aquí por usuario.
create policy "service_full_access_productos"
  on public.productos for all
  using (true) with check (true);

create policy "service_full_access_clientes"
  on public.clientes for all
  using (true) with check (true);

create policy "service_full_access_pedidos"
  on public.pedidos for all
  using (true) with check (true);

create policy "service_full_access_pedido_items"
  on public.pedido_items for all
  using (true) with check (true);

create policy "service_full_access_ventas"
  on public.ventas for all
  using (true) with check (true);

create policy "service_full_access_contabilidad"
  on public.contabilidad for all
  using (true) with check (true);
