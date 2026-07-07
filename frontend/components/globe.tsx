"use client";

import { useEffect, useRef } from "react";
import * as THREE from "three";

interface GlobeProps {
  className?: string;
}

export default function Globe({ className }: GlobeProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const container = containerRef.current;
    const width = container.clientWidth;
    const height = container.clientHeight;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
    camera.position.set(0, 0, 3.5);

    const renderer = new THREE.WebGLRenderer({
      alpha: true,
      antialias: true,
    });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    container.appendChild(renderer.domElement);

    const nvidiaGreen = new THREE.Color("#76B900");
    const sphereRadius = 1.4;

    // Group to hold all globe elements for rotation
    const globeGroup = new THREE.Group();
    scene.add(globeGroup);

    // 1. Create Dotted Grid (Latitude/Longitude graticule lines)
    const gridPoints: THREE.Vector3[] = [];
    
    // Latitudinal lines
    for (let lat = -80; lat <= 80; lat += 10) {
      const r = sphereRadius * Math.cos((lat * Math.PI) / 180);
      const y = sphereRadius * Math.sin((lat * Math.PI) / 180);
      for (let lon = 0; lon < 360; lon += 6) {
        const rad = (lon * Math.PI) / 180;
        gridPoints.push(new THREE.Vector3(r * Math.cos(rad), y, r * Math.sin(rad)));
      }
    }
    
    // Longitudinal lines
    for (let lon = 0; lon < 360; lon += 15) {
      const rad = (lon * Math.PI) / 180;
      for (let lat = -80; lat <= 80; lat += 5) {
        const r = sphereRadius * Math.cos((lat * Math.PI) / 180);
        const y = sphereRadius * Math.sin((lat * Math.PI) / 180);
        gridPoints.push(new THREE.Vector3(r * Math.cos(rad), y, r * Math.sin(rad)));
      }
    }

    const gridGeo = new THREE.BufferGeometry().setFromPoints(gridPoints);
    const gridMat = new THREE.PointsMaterial({
      color: nvidiaGreen,
      size: 0.015,
      transparent: true,
      opacity: 0.25,
    });
    const gridMesh = new THREE.Points(gridGeo, gridMat);
    globeGroup.add(gridMesh);

    // 2. Create Dotted Landmasses (Earth Continents)
    const landPoints: THREE.Vector3[] = [];
    const isLand = (lat: number, lon: number) => {
      // Approximate geographic boundaries of Earth's main continents
      // Europe & Asia (Eurasia)
      if (lat > 12 && lat < 78 && lon > -10 && lon < 145) return true;
      // Africa
      if (lat > -35 && lat < 37 && lon > -17 && lon < 51) return true;
      // North America
      if (lat > 15 && lat < 75 && lon > -168 && lon < -55) return true;
      // South America
      if (lat > -56 && lat < 13 && lon > -82 && lon < -34) return true;
      // Australia
      if (lat > -44 && lat < -10 && lon > 112 && lon < 154) return true;
      // Antarctica
      if (lat < -65) return true;
      return false;
    };

    for (let lat = -85; lat <= 85; lat += 2.5) {
      for (let lon = -180; lon < 180; lon += 2.5) {
        if (isLand(lat, lon)) {
          // Translate geographic (lat, lon) to 3D Cartesian (x, y, z)
          const phi = (90 - lat) * (Math.PI / 180);
          const theta = (lon + 180) * (Math.PI / 180);

          const x = -(sphereRadius * Math.sin(phi) * Math.cos(theta));
          const z = sphereRadius * Math.sin(phi) * Math.sin(theta);
          const y = sphereRadius * Math.cos(phi);

          landPoints.push(new THREE.Vector3(x, y, z));
        }
      }
    }

    const landGeo = new THREE.BufferGeometry().setFromPoints(landPoints);
    const landMat = new THREE.PointsMaterial({
      color: nvidiaGreen,
      size: 0.022,
      transparent: true,
      opacity: 0.7,
    });
    const landMesh = new THREE.Points(landGeo, landMat);
    globeGroup.add(landMesh);

    // 3. Floating cloud particles
    const particleCount = 250;
    const particlePoints: THREE.Vector3[] = [];
    for (let i = 0; i < particleCount; i++) {
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);
      const r = sphereRadius + 0.1 + Math.random() * 0.3;
      particlePoints.push(
        new THREE.Vector3(
          r * Math.sin(phi) * Math.cos(theta),
          r * Math.cos(phi),
          r * Math.sin(phi) * Math.sin(theta)
        )
      );
    }
    const particleGeo = new THREE.BufferGeometry().setFromPoints(particlePoints);
    const particleMat = new THREE.PointsMaterial({
      color: nvidiaGreen,
      size: 0.015,
      transparent: true,
      opacity: 0.4,
    });
    const particles = new THREE.Points(particleGeo, particleMat);
    globeGroup.add(particles);

    // 4. Subtle Glow Sphere (Atmosphere)
    const glowGeo = new THREE.SphereGeometry(sphereRadius * 1.05, 32, 32);
    const glowMat = new THREE.MeshBasicMaterial({
      color: nvidiaGreen,
      transparent: true,
      opacity: 0.03,
      wireframe: true,
    });
    const glowMesh = new THREE.Mesh(glowGeo, glowMat);
    globeGroup.add(glowMesh);

    // Interaction state
    let isDragging = false;
    let previousMousePosition = { x: 0, y: 0 };
    let rotationVelocity = { x: 0.002, y: 0 }; // Default slow rotation on Y axis

    const handleMouseDown = (e: MouseEvent) => {
      isDragging = true;
      previousMousePosition = { x: e.clientX, y: e.clientY };
    };

    const handleMouseMove = (e: MouseEvent) => {
      if (!isDragging) return;
      const deltaMove = {
        x: e.clientX - previousMousePosition.x,
        y: e.clientY - previousMousePosition.y,
      };

      // Adjust group rotation
      globeGroup.rotation.y += deltaMove.x * 0.005;
      globeGroup.rotation.x += deltaMove.y * 0.005;

      // Keep track of velocity for a nice glide effect
      rotationVelocity = {
        x: deltaMove.x * 0.001,
        y: deltaMove.y * 0.001,
      };

      previousMousePosition = { x: e.clientX, y: e.clientY };
    };

    const handleMouseUp = () => {
      isDragging = false;
    };

    const handleWheel = (e: WheelEvent) => {
      e.preventDefault();
      // Zoom bounds
      camera.position.z = Math.max(2.0, Math.min(5.5, camera.position.z + e.deltaY * 0.004));
    };

    // Attach listeners
    container.addEventListener("mousedown", handleMouseDown);
    window.addEventListener("mousemove", handleMouseMove);
    window.addEventListener("mouseup", handleMouseUp);
    container.addEventListener("wheel", handleWheel, { passive: false });

    // Touch support for mobile devices
    const handleTouchStart = (e: TouchEvent) => {
      if (e.touches.length !== 1) return;
      isDragging = true;
      previousMousePosition = { x: e.touches[0].clientX, y: e.touches[0].clientY };
    };

    const handleTouchMove = (e: TouchEvent) => {
      if (!isDragging || e.touches.length !== 1) return;
      const deltaMove = {
        x: e.touches[0].clientX - previousMousePosition.x,
        y: e.touches[0].clientY - previousMousePosition.y,
      };

      globeGroup.rotation.y += deltaMove.x * 0.005;
      globeGroup.rotation.x += deltaMove.y * 0.005;

      previousMousePosition = { x: e.touches[0].clientX, y: e.touches[0].clientY };
    };

    container.addEventListener("touchstart", handleTouchStart, { passive: true });
    window.addEventListener("touchmove", handleTouchMove, { passive: true });
    window.addEventListener("touchend", handleMouseUp);

    let animationFrameId: number;

    const animate = () => {
      animationFrameId = requestAnimationFrame(animate);

      // Auto rotation when not dragging
      if (!isDragging) {
        globeGroup.rotation.y += rotationVelocity.x;
        globeGroup.rotation.x += rotationVelocity.y;
        
        // Decay velocity back to default slow rotation
        rotationVelocity.x += (0.0015 - rotationVelocity.x) * 0.05;
        rotationVelocity.y += (0 - rotationVelocity.y) * 0.05;
      }

      // Rotate cloud particles slightly faster for independent movement
      particles.rotation.y += 0.0008;

      renderer.render(scene, camera);
    };

    animate();

    const handleResize = () => {
      const w = container.clientWidth;
      const h = container.clientHeight;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    };

    window.addEventListener("resize", handleResize);

    return () => {
      cancelAnimationFrame(animationFrameId);
      window.removeEventListener("resize", handleResize);
      container.removeEventListener("mousedown", handleMouseDown);
      window.removeEventListener("mousemove", handleMouseMove);
      window.removeEventListener("mouseup", handleMouseUp);
      container.removeEventListener("wheel", handleWheel);
      container.removeEventListener("touchstart", handleTouchStart);
      window.removeEventListener("touchmove", handleTouchMove);
      window.removeEventListener("touchend", handleMouseUp);
      
      renderer.dispose();
      if (container.contains(renderer.domElement)) {
        container.removeChild(renderer.domElement);
      }
    };
  }, []);

  return (
    <div
      ref={containerRef}
      className={className}
      style={{ width: "100%", height: "100%", minHeight: "400px" }}
    />
  );
}
