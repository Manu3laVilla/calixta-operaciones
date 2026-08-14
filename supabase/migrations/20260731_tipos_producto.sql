-- Calixta | Tipos de producto por categoría
-- Ejecutar en: Supabase Dashboard → SQL Editor → New query
--
-- Qué hace:
-- 1. Catálogo tipos_producto (CRUD desde Administración)
-- 2. productos.tipo_id → FK al catálogo (debe coincidir con la categoría)
-- 3. Accesorios no usan talla (NULL); Ropa sigue requiriendo talla

-- ─────────────────────────────────────────────────────────────────────────────
-- Catálogo: tipos de producto
-- ─────────────────────────────────────────────────────────────────────────────
create table if not exists public.tipos_producto (
  id text primary key,
  nombre text not null,
  categoria categoria_producto not null,
  activo boolean not null default true,
  orden integer not null default 0,
  fecha_registro timestamptz not null default now(),
  constraint tipos_producto_nombre_por_categoria unique (categoria, nombre)
);

create index if not exists idx_tipos_producto_categoria
  on public.tipos_producto (categoria, activo, orden);

-- ─────────────────────────────────────────────────────────────────────────────
-- Datos iniciales (ajusta nombres según tu catálogo real)
-- ─────────────────────────────────────────────────────────────────────────────
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
  ('TPO-ACC-PUL', 'Pulsera', 'Accesorio', 50)
on conflict (id) do nothing;

-- ─────────────────────────────────────────────────────────────────────────────
-- Productos: columna tipo_id
-- ─────────────────────────────────────────────────────────────────────────────
alter table public.productos
  add column if not exists tipo_id text references public.tipos_producto (id) on delete restrict;

create index if not exists idx_productos_tipo_id on public.productos (tipo_id);

-- Asignar un tipo por defecto a productos existentes (primer tipo activo de su categoría)
update public.productos p
set tipo_id = t.id
from (
  select distinct on (categoria) categoria, id
  from public.tipos_producto
  where activo = true
  order by categoria, orden, nombre
) t
where p.tipo_id is null
  and p.categoria = t.categoria;

-- Accesorios existentes: quitar talla (no aplica)
update public.productos
set talla = null
where categoria = 'Accesorio';

-- Talla nullable solo para accesorios
alter table public.productos
  alter column talla drop not null;

alter table public.productos
  drop constraint if exists productos_talla_por_categoria;

alter table public.productos
  add constraint productos_talla_por_categoria check (
    (categoria = 'Ropa' and talla is not null)
    or (categoria = 'Accesorio' and talla is null)
  );

-- Tipo obligatorio una vez migrados los datos
alter table public.productos
  alter column tipo_id set not null;

-- ─────────────────────────────────────────────────────────────────────────────
-- Validar que el tipo corresponda a la categoría del producto
-- ─────────────────────────────────────────────────────────────────────────────
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

drop trigger if exists trg_productos_validar_tipo on public.productos;

create trigger trg_productos_validar_tipo
before insert or update of tipo_id, categoria on public.productos
for each row
execute function public.validar_producto_tipo_categoria();

-- ─────────────────────────────────────────────────────────────────────────────
-- RLS
-- ─────────────────────────────────────────────────────────────────────────────
alter table public.tipos_producto enable row level security;

drop policy if exists "service_full_access_tipos_producto" on public.tipos_producto;

create policy "service_full_access_tipos_producto"
  on public.tipos_producto for all
  using (true) with check (true);
