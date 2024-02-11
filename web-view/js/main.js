import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

let camera, scene, renderer, bulbMat, light;
let ballMat, cubeMat, floorMat, lightMat;

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
    camera = setCamera();
    light = setLight(textureLoader);

    scene.add(light);

    generateCube(textureLoader);


    ballMat = new THREE.MeshStandardMaterial({
        color: 0xffffff,
        roughness: 0.5,
        metalness: 1.0
    });
    textureLoader.load('js/img/sky.jpg', function (map) {

        map.anisotropy = 4;
        map.colorSpace = THREE.SRGBColorSpace;
        ballMat.map = map;
        ballMat.needsUpdate = true;

    });

    scene.add(generateFloor(textureLoader));
    // scene.add(generateSky(textureLoader));

    const ballGeometry = new THREE.SphereGeometry(0.25, 32, 32);
    const ballMesh = new THREE.Mesh(ballGeometry, ballMat);
    ballMesh.position.set(1, 0.25, 1);
    ballMesh.rotation.y = Math.PI;
    ballMesh.castShadow = true;
    scene.add(ballMesh);

    const boxGeometry = new THREE.BoxGeometry(0.5, 0.5, 0.5);
    const boxMesh = new THREE.Mesh(boxGeometry, cubeMat);
    boxMesh.position.set(- 0.5, 0.25, - 1);
    boxMesh.castShadow = true;
    scene.add(boxMesh);

    const boxMesh2 = new THREE.Mesh(boxGeometry, cubeMat);
    boxMesh2.position.set(0, 0.25, - 5);
    boxMesh2.castShadow = true;
    scene.add(boxMesh2);

    const boxMesh3 = new THREE.Mesh(boxGeometry, cubeMat);
    boxMesh3.position.set(7, 0.25, 0);
    boxMesh3.castShadow = true;
    scene.add(boxMesh3);

    const loader = new GLTFLoader()
    // loading model
    loader.load('js/img/car/scene.gltf', (gltf) => {
        const batman = gltf.scene;
        batman.scale.setScalar(0.005);
        batman.position.x = 10;
        scene.add(batman)
    })


    renderer = new THREE.WebGLRenderer();
    renderer.shadowMap.enabled = true;
    renderer.toneMapping = THREE.ReinhardToneMapping;
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.setSize(window.innerWidth, window.innerHeight);
    container.appendChild(renderer.domElement);
    setControls();
    window.addEventListener('resize', onWindowResize);

}

function setCamera() {
    camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 100);
    camera.position.x = - 4;
    camera.position.z = 4;
    camera.position.y = 2;
    return camera;
}

function setLight(textureLoader) {
    const bulbGeometry = new THREE.SphereGeometry(1, 16, 8);

    // Erstelle ein Mesh mit der Glühbirnen-Textur
    bulbMat = new THREE.MeshStandardMaterial({
        emissive: 0xffffee,
        emissiveIntensity: 10
    });

    textureLoader.load('js/img/sky.jpg', function (map) {
        map.colorSpace = THREE.SRGBColorSpace;
        bulbMat.map = map;
        bulbMat.needsUpdate = true;
    });

    const bulbMesh = new THREE.Mesh(bulbGeometry, bulbMat);

    // Erstelle eine PointLight und füge das Mesh als Child hinzu
    const bulbLight = new THREE.PointLight(0xffee88, 1, 100, 2);
    bulbLight.add(bulbMesh);

    // Positioniere die Lichtquelle
    bulbLight.position.set(5, 5, -5);
    bulbLight.castShadow = true;
    bulbLight.power = 18000;

    return bulbLight;
}

function onWindowResize() {

    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
}

function setControls() {
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.minDistance = 1;
    controls.maxDistance = 20;
    return controls;
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
    const floorGeometry = new THREE.PlaneGeometry(100, 100);
    const floorMesh = new THREE.Mesh(floorGeometry, floorMat);
    floorMesh.receiveShadow = true;
    floorMesh.rotation.x = - Math.PI / 2.0;
    return floorMesh;
}

function generateCube(textureLoader) {
    cubeMat = new THREE.MeshStandardMaterial({
        roughness: 0.7,
        color: 0xffffff,
        bumpScale: 1,
        metalness: 0.2
    });

    textureLoader.load('js/img/sky.jpg', function (map) {

        map.wrapS = THREE.RepeatWrapping;
        map.wrapT = THREE.RepeatWrapping;
        map.anisotropy = 4;
        map.repeat.set(1, 1);
        map.colorSpace = THREE.SRGBColorSpace;
        cubeMat.map = map;
        cubeMat.needsUpdate = true;

    });
}

function generateSky(textureLoader) {
    const skyboxTexture = textureLoader.load([
        'js/img/night.jpg'
    ]);

    const skyboxMaterial = new THREE.MeshBasicMaterial({
        map: skyboxTexture,
        side: THREE.BackSide, // Wichtig, um die Skybox von innen zu sehen
    });

    const skyboxGeometry = new THREE.BoxGeometry(100, 100, 100);
    const skyboxMesh = new THREE.Mesh(skyboxGeometry, skyboxMaterial);
    return skyboxMesh;
}

//

function animate() {

    requestAnimationFrame(animate);
    render();

}

function render() {

    renderer.toneMappingExposure = Math.pow(params.exposure, 5.0); // to allow for very bright scenes.
    light.castShadow = params.shadows;

    if (params.shadows !== previousShadowMap) {
        ballMat.needsUpdate = true;
        cubeMat.needsUpdate = true;
        floorMat.needsUpdate = true;
        previousShadowMap = params.shadows;
    }
    renderer.render(scene, camera);
}
