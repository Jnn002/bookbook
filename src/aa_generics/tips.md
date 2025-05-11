# Guía Genérica de Validación por Capas en Arquitectura Hexagonal

Este documento describe los tipos de validaciones comunes y la capa arquitectónica donde típicamente se realizan en un sistema backend que sigue principios de Arquitectura Hexagonal (Puertos y Adaptadores).

## Capa de Infraestructura - Adaptadores de Entrada (Ej: API Web con FastAPI/Pydantic)

**Propósito Principal:** Validar la **forma, estructura y tipos básicos** de los datos que ingresan al sistema desde el exterior, según el contrato del adaptador (ej. contrato de API). Proteger el sistema de datos malformados en la frontera.

**Tipos de Validaciones Comunes:**

1.  **Presencia de Campos (Requeridos vs. Opcionales):**
    *   Verificar que todos los campos marcados como obligatorios en el DTO/Schema de entrada estén presentes.
    *   Manejar correctamente los campos opcionales.

2.  **Tipo de Dato Básico:**
    *   Asegurar que los datos coincidan con los tipos esperados (ej. string, integer, float, boolean, list, dictionary).
    *   Ej: Un campo numérico no debe ser un string, una lista esperada no debe ser un objeto.

3.  **Formato Específico del Tipo:**
    *   **Strings:**
        *   Formato de Email.
        *   Formato de UUID.
        *   Formato de URL.
        *   Formato de Fecha/Hora (ej. ISO 8601).
        *   Coincidencia con expresiones regulares (regex) para patrones específicos.
    *   **Números:**
        *   Si es un entero o un decimal con cierta precisión.

4.  **Restricciones de Valor Simples (Literales o de Rango):**
    *   **Strings:**
        *   Longitud mínima y/o máxima.
        *   Valores permitidos de una enumeración (enum).
    *   **Números:**
        *   Valor mínimo (ej. `gt=0`, `ge=0`).
        *   Valor máximo.
        *   Múltiplo de un número.
    *   **Fechas:**
        *   Fecha en el pasado (`PastDate`).
        *   Fecha en el futuro (`FutureDate`).
        *   Fecha dentro de un rango específico.
    *   **Listas/Arrays:**
        *   Número mínimo/máximo de ítems (`min_items`, `max_items`).
        *   Unicidad de los ítems (si aplica).

5.  **Coherencia Estructural del Payload:**
    *   Si se esperan objetos anidados, verificar su estructura.

**Herramientas Típicas:** Librerías de validación de esquemas como Pydantic (para FastAPI), Marshmallow, Cerberus, etc.

**Resultado de Falla:** Generalmente, un error de "datos no procesables" (ej. HTTP 422) devuelto al cliente, sin que la lógica de aplicación o dominio se ejecute.

---

## Capa de Aplicación (Servicios de Aplicación / Casos de Uso)

**Propósito Principal:** Orquestar los casos de uso, validar el **flujo de la operación**, la **existencia de entidades requeridas**, y los **permisos** del actor. Puede realizar validaciones que requieran acceso a repositorios u otros servicios.

**Tipos de Validaciones Comunes:**

1.  **Existencia de Entidades (Pre-condiciones del Caso de Uso):**
    *   Verificar que las entidades referenciadas por IDs en la solicitud existen en el sistema (ej. ¿existe el usuario con `user_id` X?, ¿existe el producto con `product_id` Y?).
    *   Esto se hace consultando los repositorios (puertos de salida).

2.  **Validación de Permisos y Autorización:**
    *   ¿Tiene el usuario/actor actual los permisos necesarios para ejecutar esta acción o acceder/modificar este recurso?
    *   (A menudo, parte de esto puede ser manejado por middleware o decoradores en la capa de adaptadores web antes de llegar al servicio de aplicación).

3.  **Validación de Estado para la Operación:**
    *   ¿Está la entidad principal en un estado que permite esta operación? (Ej. ¿Se puede cancelar un pedido si ya fue enviado? ¿Se puede editar un documento si está bloqueado por otro usuario?).
    *   Esto puede implicar consultar el estado actual de un objeto de dominio.

4.  **Unicidad a Nivel de Aplicación/Sistema (que no son simples constraints de BD):**
    *   Verificar si ya existe un recurso con ciertos atributos únicos antes de crear uno nuevo (ej. ¿ya existe un usuario con este email o nombre de usuario?).
    *   Se consulta el repositorio.

5.  **Coherencia entre Diferentes Entradas o Recursos:**
    *   Si una operación involucra múltiples IDs o datos, verificar que sean compatibles entre sí según la lógica de la aplicación (ej. ¿pertenece el item X a la orden Y?).

**Herramientas Típicas:** Lógica condicional en los servicios de aplicación, uso de los resultados de los puertos de salida.

**Resultado de Falla:** Excepciones de aplicación específicas (ej. `ResourceNotFoundAppException`, `PermissionDeniedAppException`, `OperationNotAllowedAppException`), que luego son mapeadas a respuestas HTTP adecuadas por el adaptador web.

---

## Capa de Dominio (Modelos de Dominio POPOs / Servicios de Dominio)

**Propósito Principal:** Mantener la **integridad, consistencia y validez interna** de los objetos de dominio según las **reglas de negocio fundamentales**. Proteger las invariantes del dominio.

**Tipos de Validaciones Comunes:**

1.  **Invariantes del Objeto:**
    *   Reglas que siempre deben ser verdaderas para que un objeto de dominio sea considerado válido (ej. el precio de un producto no puede ser negativo, el stock no puede ser menor que cero).
    *   Se verifican típicamente en el constructor (`__init__`/`__post_init__`) y en cualquier método que modifique el estado del objeto.

2.  **Valores Semánticos de los Atributos:**
    *   Aunque la capa de infraestructura valide el tipo/formato, el dominio valida el *significado* o restricciones de negocio.
    *   Ej: Un rating debe estar entre 1 y 5 (el negocio define este rango). Un título no puede ser solo espacios en blanco. Una edad debe ser positiva.
    *   Normalización de datos (ej. convertir un email o tag a minúsculas).

3.  **Consistencia Interna del Estado del Objeto:**
    *   Reglas sobre cómo los diferentes atributos de un objeto se relacionan entre sí (ej. la fecha de fin de una promoción no puede ser anterior a su fecha de inicio).

4.  **Transiciones de Estado Válidas:**
    *   Si un objeto de dominio tiene un ciclo de vida con diferentes estados, validar que las transiciones entre estados sean permitidas (ej. un pedido solo puede pasar de "pendiente" a "pagado", no directamente a "enviado").

5.  **Reglas de Negocio Complejas (Intra-Objeto o con Colaboradores Cercanos):**
    *   Lógica que define cómo el objeto debe comportarse o qué condiciones debe cumplir según las políticas del negocio.
    *   Ej: Un descuento aplicado a un `DomainOrderItem` no puede exceder el X% del precio original del producto.

**Herramientas Típicas:** Lógica condicional dentro de los métodos de los POPOs, `asserts` (para invariantes durante el desarrollo), excepciones de dominio personalizadas. Servicios de Dominio para reglas que involucran múltiples objetos de dominio.

**Resultado de Falla:** Lanzamiento de excepciones de dominio específicas (ej. `InvalidPriceDomainException`, `StockUnavailableDomainException`, `IllegalStateTransitionDomainException`). Estas son capturadas y manejadas (posiblemente re-lanzadas o mapeadas) por la capa de aplicación.

---

Esta separación ayuda a que cada capa se enfoque en su nivel de abstracción y responsabilidad, creando un sistema más robusto y mantenible.