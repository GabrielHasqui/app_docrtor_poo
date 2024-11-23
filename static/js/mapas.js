// Google Maps API Script
<script src="https://maps.googleapis.com/maps/api/js?key=AIzaSyCrn6f9kWfWm4uMzHsJUHmk2O9jnfrErJ0&callback=initMap&libraries=places" async defer></script>

// Variables globales
let map, marker, geocoder, autocomplete;

// Función de inicialización del mapa
function initMap() {
    // Configuración inicial
    const initialLocation = { lat: -2.170998, lng: -79.922359 };
    const latInput = document.getElementById('{{ form.latitud.id_for_label }}');
    const lngInput = document.getElementById('{{ form.longitud.id_for_label }}');
    const addressInput = document.getElementById('{{ form.direccion.id_for_label }}');

    // Inicialización del mapa
    map = new google.maps.Map(document.getElementById("map"), {
        center: initialLocation,
        zoom: 13,
    });

    // Configuración del marcador
    marker = new google.maps.Marker({
        position: initialLocation,
        map: map,
        draggable: true,
    });

    // Inicialización de servicios de Google Maps
    geocoder = new google.maps.Geocoder();
    autocomplete = new google.maps.places.Autocomplete(document.getElementById("addressInput"));
    autocomplete.bindTo("bounds", map);

    // Event Listeners
    autocomplete.addListener("place_changed", function() {
        const place = autocomplete.getPlace();
        if (!place.geometry || !place.geometry.location) {
            alert("La ubicación ingresada no es válida.");
            return;
        }

        map.setCenter(place.geometry.location);
        marker.setPosition(place.geometry.location);
        latInput.value = place.geometry.location.lat().toFixed(5);
        lngInput.value = place.geometry.location.lng().toFixed(5);
        addressInput.value = place.formatted_address;
    });

    google.maps.event.addListener(marker, "dragend", function() {
        const position = marker.getPosition();
        latInput.value = position.lat().toFixed(5);
        lngInput.value = position.lng().toFixed(5);
        geocodePosition(position);
    });
}

// Función para geocodificar la posición
function geocodePosition(position) {
    geocoder.geocode({ location: position }, function(results, status) {
        if (status === google.maps.GeocoderStatus.OK) {
            const addressInput = document.getElementById('{{ form.direccion.id_for_label }}');
            if (results[0]) {
                addressInput.value = results[0].formatted_address;
            }
        }
    });
}

// Función para guardar la ubicación
function saveLocation() {
    const latInput = document.getElementById('{{ form.latitud.id_for_label }}');
    const lngInput = document.getElementById('{{ form.longitud.id_for_label }}');
    const addressInput = document.getElementById('{{ form.direccion.id_for_label }}');

    if (!latInput.value || !lngInput.value || !addressInput.value) {
        alert("Selecciona una ubicación en el mapa.");
        return;
    }
    
    const mapModal = document.getElementById("mapModal");
    const bootstrapModal = bootstrap.Modal.getInstance(mapModal);
    if (bootstrapModal) {
        bootstrapModal.hide();
    }

    setTimeout(() => {
        document.body.classList.remove('modal-open');
        document.querySelector('.modal-backdrop').remove();
    }, 500);
}
