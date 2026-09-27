import { FIELD, goalPosts, type Point } from "./scenario";

export const viewBox = { width: FIELD.width, height: FIELD.length - FIELD.halfLine };

// The attacking direction points up on screen; both SVG axes use one unit per meter.
export function toSvg(point: Point): Point {
  return { x: point.y, y: FIELD.length - point.x };
}

export function fromSvg(point: Point): Point {
  return { x: FIELD.length - point.y, y: point.x };
}

export function shotDistance(shooter: Point): number {
  return Math.hypot(FIELD.length - shooter.x, FIELD.centerY - shooter.y);
}

export function shotAngle(shooter: Point): number {
  const [left, right] = goalPosts;
  const a = { x: left.x - shooter.x, y: left.y - shooter.y };
  const b = { x: right.x - shooter.x, y: right.y - shooter.y };
  const cross = Math.abs(a.x * b.y - a.y * b.x);
  const dot = a.x * b.x + a.y * b.y;
  return (Math.atan2(cross, dot) * 180) / Math.PI;
}
