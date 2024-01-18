import * as THREE from 'three';

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
camera.position.z = 5;

const renderer = new THREE.WebGLRenderer();
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

const geometry = new THREE.BoxGeometry(1, 1, 1);
const material = new THREE.MeshBasicMaterial({ color: 0x00ff00 });
// const cube = new THREE.Mesh(geometry, material);
// scene.add(cube);

function createFloor() {
    // PlaneGeometry für den Boden erstellen
    let floorGeometry = new THREE.PlaneGeometry(window.innerWidth, 100, 10, 10);

    // MeshBasicMaterial für den Boden erstellen
    let floorMaterial = new THREE.MeshBasicMaterial({ color: 0x0000ff, side: THREE.DoubleSide });

    // Mesh erstellen, indem Sie Geometry und Material kombinieren
    let floor = new THREE.Mesh(floorGeometry, floorMaterial);

    // Position des Bodens anpassen, um ihn unter dem Würfel zu platzieren
    floor.position.y = -2;

    // Drehen Sie den Boden, um ihn flach auf den Boden zu legen
    floor.rotation.x = Math.PI / 2;

    // Fügen Sie den Boden zur Szene hinzu
    scene.add(floor);
}

function createPoint() {
    const pointGeometry = new THREE.BufferGeometry();
    const materialPoint = new THREE.PointsMaterial({ color: 'red' }); // Änderung zu THREE.PointsMaterial
    const vertices = new Float32Array([5, 3, 0]); // Die Koordinaten des Punkts
    pointGeometry.setAttribute('position', new THREE.BufferAttribute(vertices, 3));
    // Erstellen Sie das Points-Objekt
    const point = new THREE.Points(pointGeometry, materialPoint);
    // Fügen Sie den Punkt zur Szene hinzu
    scene.add(point);
}

function animate() {
    requestAnimationFrame(animate);
    // cube.rotation.x += 0.01;
    // cube.rotation.y += 0.01;
    renderer.render(scene, camera);
}
createFloor();
createPoint();
animate();
