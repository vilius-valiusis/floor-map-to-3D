var container, stats;
var camera, scene, renderer, controls;
var group;

init();
animate();
function init() {
    container = document.createElement( 'div' );
    document.body.appendChild( container );
    var info = document.createElement( 'div' );
    info.style.position = 'absolute';
    info.style.top = '10px';
    info.style.width = '100%';
    info.style.textAlign = 'center';
    info.innerHTML = 'Simple procedurally-generated shapes<br/>Drag to spin';
    container.appendChild( info );

    renderer = new THREE.WebGLRenderer({antialias: true});
    renderer.setSize( window.innerWidth, window.innerHeight );
    document.body.appendChild( renderer.domElement );

    scene = new THREE.Scene();
    scene.background = new THREE.Color( 0xf0f0f0 );

    camera = new THREE.PerspectiveCamera( 65, window.innerWidth / window.innerHeight, 1, 3000 );
    camera.position.set( 0, 100, 1500 );
    controls = new THREE.OrbitControls(camera)
    controls.update();

    var light = new THREE.PointLight( 0xffffff, 0.8 );

    group = new THREE.Group();
    group.position.y = 0;

    camera.add( light );
    scene.add( group );
    scene.add( camera );

    var walls = 'input/walls.json';
    var doors = 'input/doors.json';
    var windows = 'input/windows.json';

    loadJSON(walls,function(response) {
        // Parse JSON string into object
        var actual_JSON = JSON.parse(response);
        drawWall(actual_JSON)
    });

    loadJSON(doors,function(response) {
        // Parse JSON string into object
        var actual_JSON = JSON.parse(response);
        drawDoor(actual_JSON)
    });
    loadJSON(windows,function(response) {
        // Parse JSON string into object
        var actual_JSON = JSON.parse(response);
        drawWindows(actual_JSON)
    });

}

function drawWall(walls){
    var extrudeSettings = { amount: 200, bevelEnabled: true, bevelSegments: 2, steps: 2, bevelSize: 1, bevelThickness: 1 };
    var floor_extrudeSettings = { amount: 10, bevelEnabled: true, bevelSegments: 2, steps: 2, bevelSize: 1, bevelThickness: 1 };
    var big_y = 0, small_y = 0, big_x = 0, small_x = 0

    for(var i in walls){
        var wallshape = new THREE.Shape();
        wallshape.moveTo(walls[i][0][0],walls[i][0][1])
        for(var x in walls[i]){
            wallshape.lineTo(walls[i][x][0],walls[i][x][1])
                if( walls[i][x][0] < small_x || small_x === 0){
                    small_x = walls[i][x][0]
                }
                if( walls[i][x][1] < small_y || small_y === 0){
                    small_y = walls[i][x][1]
                }
                if( walls[i][x][0] > big_x || big_x === 0){
                    big_x = walls[i][x][0]
                }
                if( walls[i][x][1] > big_y || big_y === 0){
                    big_y = walls[i][x][1]
                }
            }
            addShape( wallshape,extrudeSettings, 0xf08000, -750, -750, 0, 0, 0, 0, 1);
    }
    // Draw a simple all encompassing floor
    var texture = new THREE.TextureLoader().load( "textures/retina_wood.png" );
    var floor_shape = new THREE.Shape()
    floor_shape.moveTo(small_x,small_y)
    floor_shape.lineTo(small_x,big_y)
    floor_shape.lineTo(big_x,big_y)
    floor_shape.lineTo(big_x,small_x)
    addShape( floor_shape,floor_extrudeSettings, 0x6e2c00 , -750, -750, -10, 0, 0, 0, 1);

    wallshape.moveTo(walls[i][0][0],walls[i][0][1])

}

function drawDoor(doors){
    var extrudeSettings = { amount: 200, bevelEnabled: true, bevelSegments: 2, steps: 2, bevelSize: 1, bevelThickness: 1 };
    for(var i in doors){
        var doorShape = new THREE.Shape();
        doorShape.moveTo(doors[i][0][0],doors[i][0][1])
        for(var x in doors[i]){
            doorShape.lineTo(doors[i][x][0],doors[i][x][1])
        }
        addShape( doorShape,extrudeSettings, 0xf302013, -750, -750, 0, 0, 0, 0, 1);

    }
}

function drawWindows(windows){
    var extrudeSettings = { amount: 40, bevelEnabled: true, bevelSegments: 2, steps: 2, bevelSize: 1, bevelThickness: 1 };
    for(var i in windows){
        var windowShape = new THREE.Shape();
        windowShape.moveTo(windows[i][0][0],windows[i][0][1])
        for(var x in windows[i]){
            windowShape.lineTo(windows[i][x][0],windows[i][x][1])
        }
        addShape( windowShape,extrudeSettings, 0xf08000, -750, -750, 0, 0, 0, 0, 1);
        addShape( windowShape,extrudeSettings, 0xf08000, -750, -750, 160, 0, 0, 0, 1);

    }
}

function addShape( shape, extrudeSettings, color, x, y, z, rx, ry, rz, s ) {

    var geometry = new THREE.ExtrudeGeometry( shape, extrudeSettings );
    var mesh = new THREE.Mesh( geometry, new THREE.MeshPhongMaterial( {color: color}));
    mesh.position.set(x, y, z);
    mesh.rotation.set( rx, ry, rz );
    mesh.scale.set( s, s, s );
    group.add( mesh );
}

function animate() {
    requestAnimationFrame( animate );
    controls.update();
    renderer.render( scene, camera );
}

function loadJSON(location, callback) {
    var xobj = new XMLHttpRequest();
    xobj.overrideMimeType("application/json");
    xobj.open('GET', location, true); // Replace 'my_data' with the path to your file
    xobj.onreadystatechange = function () {
        if (xobj.readyState == 4 && xobj.status == "200") {
            // Required use of an anonymous callback as .open will NOT return a value but simply returns undefined in asynchronous mode
            callback(xobj.responseText);
        }
    };
    xobj.send(null);
}

