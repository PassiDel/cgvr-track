import * as THREE from 'three';
import {GLTFLoader} from 'three/examples/jsm/loaders/GLTFLoader';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';
import {Sky} from 'three/addons/objects/Sky.js';
import {FontLoader} from 'three/addons/loaders/FontLoader.js';
import {TextGeometry} from 'three/addons/geometries/TextGeometry.js';

let camera, controls,  scene, renderer, bulbMat, light;
let ballMat, cubeMat, floorMat, drivingMat, car;

let previousShadowMap = false;

const params = {
    shadows: true,
    exposure: 0.68,
};

init();
animate();

function init() {

    const container = document.getElementById('container');
    const textureLoader = new THREE.TextureLoader();

    scene = new THREE.Scene();
    // scene.background = new THREE.Color(0x87ceeb);

    scene.add(generateSky());

    camera = setCamera();
    light = setLight(textureLoader);
    scene.add(light);

    // createFence();

    scene.add(generateFloor(textureLoader));
    scene.add(generateDrivingArea(textureLoader));

    const loader = new GLTFLoader()
    // loading model
    loader.load('js/img/car/scene.gltf', (gltf) => {
        car = gltf.scene;
        car.scale.setScalar(0.005);
        car.position.x = 10;
        scene.add(car)
    })

    loader.load('js/img/tree/scene.gltf', (gltf) => {
        let house = gltf.scene;
        house.scale.setScalar(2);
        house.position.x = 30;
        scene.add(house)
    })


    renderer = new THREE.WebGLRenderer();
    renderer.shadowMap.enabled = true;
    renderer.toneMapping = THREE.ReinhardToneMapping;
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.setSize(window.innerWidth, window.innerHeight);
    container.appendChild(renderer.domElement);
    setControls();
    window.addEventListener('resize', onWindowResize);


    const evtSource = new EventSource('http://127.0.0.1:5000/stream');
    evtSource.addEventListener('data', e => {
        const [x, z, y] = JSON.parse(e.data)
        if (car && car.position) {
            car.position.z = z;
            car.position.y = 0;
            car.position.x = -x;

            console.log(camera.position)
            // controls.target.z = z-60;
            // controls.target.y = y+10;
            // controls.target.x = x+10;
        }
    })

    console.log(controls)

}

function setCamera() {
    camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 100);
    camera.position.x = 0;
    camera.position.z = -10;
    camera.position.y = 0;
    return camera;
}

function setLight() {
    const light = new THREE.AmbientLight(0xffffff, 50)
    return light;
}

function onWindowResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
}

function setControls() {
    controls = new OrbitControls(camera, renderer.domElement);
    controls.listenToKeyEvents( window );
    controls.minDistance = 1;
    controls.maxDistance = 20;
    return controls;
}

function createText(text, position) {
    var loader = new FontLoader();

    loader.load('https://threejsfundamentals.org/threejs/resources/threejs/fonts/helvetiker_regular.typeface.json', function (font) {
        var textGeometry = new TextGeometry(text, {
            font: font,
            size: 0.2,
            height: 0.05,
        });

        var textMaterial = new THREE.MeshBasicMaterial({color: 0x000000});
        var textMesh = new THREE.Mesh(textGeometry, textMaterial);
        textMesh.position.copy(position);
        scene.add(textMesh);
    });
}


function createFence() {
    // Erstellen Sie den Zaun
    var fenceGeometry = new THREE.BoxGeometry(0.1, 1, 0.1); // Ändern Sie die Größe entsprechend Ihren Anforderungen
    var fenceMaterial = new THREE.MeshBasicMaterial({color: 0xff0000});

    for (var i = -10; i <= 10; i++) {
        var fence = new THREE.Mesh(fenceGeometry, fenceMaterial);
        fence.position.set(0, 0.5, i); // Platzieren Sie den Zaun entsprechend
        scene.add(fence);
    }

    for (var i = -9; i < 10; i++) {
        var fence = new THREE.Mesh(fenceGeometry, fenceMaterial);
        fence.position.set(20, 0.5, i); // Platzieren Sie den Zaun entsprechend
        scene.add(fence);
    }

    for (var i = 0; i <= 20; i++) {
        var fence = new THREE.Mesh(fenceGeometry, fenceMaterial);
        fence.position.set(i, 0.5, -10); // Platzieren Sie den Zaun entsprechend
        scene.add(fence);
    }

    for (var i = 0; i <= 20; i++) {
        var fence = new THREE.Mesh(fenceGeometry, fenceMaterial);
        fence.position.set(i, 0.5, 10); // Platzieren Sie den Zaun entsprechend
        scene.add(fence);
    }

}

function generateFloor(textureLoader) {

    floorMat = new THREE.MeshStandardMaterial({
        roughness: 0.8,
        color: 0xffffff,
        metalness: 0.2,
        bumpScale: 1
    });
    textureLoader.load('js/img/wiese_2.jpg', function (map) {
        map.wrapS = THREE.RepeatWrapping;
        map.wrapT = THREE.RepeatWrapping;
        map.repeat.set(100, 100);
        map.colorSpace = THREE.SRGBColorSpace;
        floorMat.map = map;
        floorMat.needsUpdate = true;

    });
    const floorGeometry = new THREE.PlaneGeometry(400, 400);
    const floorMesh = new THREE.Mesh(floorGeometry, floorMat);
    floorMesh.receiveShadow = true;
    floorMesh.rotation.x = -Math.PI / 2.0;
    return floorMesh;
}

function generateDrivingArea(textureLoader) {

    drivingMat = new THREE.MeshStandardMaterial({
        roughness: 0.8,
        color: 0xffffff,
        metalness: 0.2,
        bumpScale: 1
    });
    textureLoader.load('js/img/street.jpg', function (map) {
        map.wrapS = THREE.RepeatWrapping;
        map.wrapT = THREE.RepeatWrapping;
        map.repeat.set(10, 10);
        map.colorSpace = THREE.SRGBColorSpace;
        drivingMat.map = map;
        drivingMat.needsUpdate = true;

    });
    const floorGeometry = new THREE.PlaneGeometry(20, 20);
    const floorMesh = new THREE.Mesh(floorGeometry, drivingMat);
    floorMesh.position.x = 10;
    floorMesh.position.y = 0.0001;
    floorMesh.receiveShadow = true;
    floorMesh.rotation.x = -Math.PI / 2.0;
    return floorMesh;
}

function generateSky() {
    const sky = new Sky();
    sky.scale.setScalar(10000);

    const skyUniforms = sky.material.uniforms;

    skyUniforms['turbidity'].value = 10;
    skyUniforms['rayleigh'].value = 2;
    skyUniforms['mieCoefficient'].value = 0.005;
    skyUniforms['mieDirectionalG'].value = 0.8;
    const phi = THREE.MathUtils.degToRad(-80);
    const theta = THREE.MathUtils.degToRad(-20);
    let sun = new THREE.Vector3();

    sun.setFromSphericalCoords(1, phi, theta);

    sky.material.uniforms['sunPosition'].value.copy(sun);
    return sky;
}

//

function animate() {

    requestAnimationFrame(animate);
    render();

}

function render() {
    controls.update()

    renderer.toneMappingExposure = Math.pow(params.exposure, 5.0); // to allow for very bright scenes.
    // light.castShadow = params.shadows;

    if (params.shadows !== previousShadowMap) {
        floorMat.needsUpdate = true;
        previousShadowMap = params.shadows;
    }
    renderer.render(scene, camera);
}
