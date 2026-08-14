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
-- estado_pedido enum legacy (pedidos.estado es text → estados_pedido.nombre)
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
-- Tipos de producto (por categoría; administrables desde el módulo Administración)
-- ─────────────────────────────────────────────────────────────────────────────
create table public.tipos_producto (
  id text primary key,
  nombre text not null,
  categoria categoria_producto not null,
  activo boolean not null default true,
  orden integer not null default 0,
  fecha_registro timestamptz not null default now(),
  constraint tipos_producto_nombre_por_categoria unique (categoria, nombre)
);

create index idx_tipos_producto_categoria on public.tipos_producto (categoria, activo, orden);

insert into public.tipos_producto (id, nombre, categoria, orden) values
  ('TPO-ROPA-CAM', 'Camiseta', 'Ropa', 10),
  ('TPO-ROPA-CMS', 'Camisa', 'Ropa', 20),
  ('TPO-ROPA-PAN', 'Pantalón', 'Ropa', 30),
  ('TPO-ROPA-VES', 'Vestido', 'Ropa', 40),
  ('TPO-ROPA-BLA', 'Blusa', 'Ropa', 50),
  ('TPO-ACC-TBG', 'Totebag', 'Accesorio', 10),
  ('TPO-ACC-PAN', 'Pañoleta', 'Accesorio', 20),
  ('TPO-ACC-COL', 'Collar', 'Accesorio', 30),
  ('TPO-ACC-ARE', 'Aretes', 'Accesorio', 40),
  ('TPO-ACC-PUL', 'Pulsera', 'Accesorio', 50);

-- ─────────────────────────────────────────────────────────────────────────────
-- Productos
-- ─────────────────────────────────────────────────────────────────────────────
create table public.productos (
  id text primary key,
  referencia text not null,
  nombre text not null,
  color text not null default '',
  talla talla_producto,
  categoria categoria_producto not null,
  tipo_id text not null references public.tipos_producto (id) on delete restrict,
  descripcion text not null default '',
  stock integer not null default 0 check (stock >= 0),
  stock_minimo integer not null default 0 check (stock_minimo >= 0),
  precio numeric(12, 2) not null default 0 check (precio >= 0),
  activo boolean not null default true,
  fecha_registro timestamptz not null default now(),
  constraint productos_talla_por_categoria check (
    (categoria = 'Ropa' and talla is not null)
    or (categoria = 'Accesorio' and talla is null)
  )
);

create index idx_productos_referencia on public.productos (referencia);
create index idx_productos_activo on public.productos (activo);
create index idx_productos_stock_minimo on public.productos (stock_minimo);
create index idx_productos_tipo_id on public.productos (tipo_id);

-- ─────────────────────────────────────────────────────────────────────────────
-- Tipos de ingreso (contabilidad; administrables)
-- ─────────────────────────────────────────────────────────────────────────────
create table public.tipos_ingreso (
  id text primary key,
  nombre text not null unique,
  activo boolean not null default true,
  orden integer not null default 0,
  fecha_registro timestamptz not null default now()
);

create index idx_tipos_ingreso_activo on public.tipos_ingreso (activo, orden);

insert into public.tipos_ingreso (id, nombre) values
  ('TIN-CAP', 'Capital'),
  ('TIN-INV', 'Inversión'),
  ('TIN-OTR', 'Otros ingresos');

-- ─────────────────────────────────────────────────────────────────────────────
-- Tipos de gasto (contabilidad; administrables)
-- ─────────────────────────────────────────────────────────────────────────────
create table public.tipos_gasto (
  id text primary key,
  nombre text not null unique,
  activo boolean not null default true,
  fecha_registro timestamptz not null default now()
);

create index idx_tipos_gasto_activo on public.tipos_gasto (activo, nombre);

insert into public.tipos_gasto (id, nombre) values
  ('TGA-INS', 'Insumos'),
  ('TGA-EQU', 'Equipos'),
  ('TGA-OTR', 'Otros gastos');

-- ─────────────────────────────────────────────────────────────────────────────
-- Estados de pedido (flujo configurable)
-- ─────────────────────────────────────────────────────────────────────────────
create table public.estados_pedido (
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

create index idx_estados_pedido_activo on public.estados_pedido (activo, orden);

insert into public.estados_pedido (
  id, nombre, orden, genera_venta, revierte_venta, es_inicial, bloquea_edicion
) values
  ('EST-REC', 'Recibido', 10, false, false, true, false),
  ('EST-PAG', 'Pago Confirmado', 20, false, false, false, false),
  ('EST-ENV', 'Envío Agendado', 30, false, false, false, false),
  ('EST-ENT', 'Entregado', 40, true, false, false, true),
  ('EST-CAN', 'Cancelado', 50, false, true, false, true);

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
  estado text not null default 'Recibido' references public.estados_pedido (nombre) on delete restrict,
  venta_registrada boolean not null default false,
  stock_reservado boolean not null default false,
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
  fecha_actualizacion timestamptz not null default now()
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

create or replace function public.validar_producto_tipo_categoria()
returns trigger
language plpgsql
as $$
declare
  tipo_categoria categoria_producto;
begin
  if new.tipo_id is null then
    raise exception 'El producto debe tener un tipo asignado.';
  end if;

  select t.categoria
  into tipo_categoria
  from public.tipos_producto t
  where t.id = new.tipo_id;

  if tipo_categoria is null then
    raise exception 'Tipo de producto inválido: %', new.tipo_id;
  end if;

  if tipo_categoria <> new.categoria then
    raise exception
      'El tipo % pertenece a %, pero el producto es %.',
      new.tipo_id, tipo_categoria, new.categoria;
  end if;

  return new;
end;
$$;

create trigger trg_productos_validar_tipo
before insert or update of tipo_id, categoria on public.productos
for each row
execute function public.validar_producto_tipo_categoria();

-- ─────────────────────────────────────────────────────────────────────────────
-- Alertas por correo (configuración administrable)
-- ─────────────────────────────────────────────────────────────────────────────
create table public.config_alertas_email (
  id text primary key default 'DEFAULT',
  activo boolean not null default false,
  envios_por_dia integer not null default 1 check (envios_por_dia between 1 and 3),
  horario_1 time not null default '08:00',
  horario_2 time not null default '14:00',
  horario_3 time not null default '18:00',
  solo_si_hay_alertas boolean not null default true,
  zona_horaria text not null default 'America/Bogota',
  fecha_actualizacion timestamptz not null default now()
);

insert into public.config_alertas_email (id) values ('DEFAULT');

create table public.alertas_destinatarios (
  id text primary key,
  email text not null,
  nombre text not null default '',
  activo boolean not null default true,
  fecha_registro timestamptz not null default now(),
  constraint alertas_destinatarios_email_unique unique (email)
);

create index idx_alertas_destinatarios_activo on public.alertas_destinatarios (activo, email);

create table public.alertas_envios_log (
  id bigserial primary key,
  slot integer not null check (slot between 1 and 3),
  fecha date not null,
  enviado_en timestamptz not null default now(),
  destinatarios text not null default '',
  productos_count integer not null default 0,
  exito boolean not null default true,
  mensaje text not null default '',
  constraint alertas_envios_log_fecha_slot_unique unique (fecha, slot)
);

create index idx_alertas_envios_log_enviado_en on public.alertas_envios_log (enviado_en desc);

-- ─────────────────────────────────────────────────────────────────────────────
-- Seguridad (RLS)
-- App interna: acceso solo con service_role desde el backend (Python).
-- ─────────────────────────────────────────────────────────────────────────────
alter table public.tipos_producto enable row level security;
alter table public.tipos_ingreso enable row level security;
alter table public.tipos_gasto enable row level security;
alter table public.estados_pedido enable row level security;
alter table public.productos enable row level security;
alter table public.clientes enable row level security;
alter table public.pedidos enable row level security;
alter table public.pedido_items enable row level security;
alter table public.ventas enable row level security;
alter table public.contabilidad enable row level security;
alter table public.config_alertas_email enable row level security;
alter table public.alertas_destinatarios enable row level security;
alter table public.alertas_envios_log enable row level security;

-- Políticas permisivas para el rol autenticado de servicio (service_role bypass RLS).
-- Si más adelante usas auth de Supabase, restringe aquí por usuario.
create policy "service_full_access_tipos_producto"
  on public.tipos_producto for all
  using (true) with check (true);

create policy "service_full_access_tipos_ingreso"
  on public.tipos_ingreso for all
  using (true) with check (true);

create policy "service_full_access_tipos_gasto"
  on public.tipos_gasto for all
  using (true) with check (true);

create policy "service_full_access_estados_pedido"
  on public.estados_pedido for all
  using (true) with check (true);

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

create policy "service_full_access_config_alertas_email"
  on public.config_alertas_email for all
  using (true) with check (true);

create policy "service_full_access_alertas_destinatarios"
  on public.alertas_destinatarios for all
  using (true) with check (true);

create policy "service_full_access_alertas_envios_log"
  on public.alertas_envios_log for all
  using (true) with check (true);
