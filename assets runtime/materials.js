/** Same-origin browser reference implementation. Canvas output uses straight RGBA.
 * Load only equipped models. Call on appearance changes, not every game frame.
 */
export class CommanderMaterials {
  static async load(root = './') {
    const url = new URL(root, document.baseURI);
    const response = await fetch(new URL('catalog.json', url));
    if (!response.ok) throw new Error(`Catalog HTTP ${response.status}`);
    return new CommanderMaterials(url, await response.json());
  }
  constructor(root, catalog) {
    this.root = root; this.catalog = catalog;
    this.models = new Map(catalog.models.map(m => [m.id, m]));
    this.textures = new Map(catalog.textures.map(t => [t.id, t]));
    this.palettes = new Map(catalog.palettes.map(p => [p.id, p]));
    this.images = new Map(); this.pixels = new Map();
  }
  // Bounded CPU caches. The game owns and disposes uploaded GPU textures.
  remember(map, key, value, limit) {
    if (map.size >= limit) map.delete(map.keys().next().value);
    map.set(key, value); return value;
  }
  async image(file) {
    if (this.images.has(file)) return this.images.get(file);
    const pending = new Promise((resolve, reject) => {
      const im = new Image(); im.onload = () => resolve(im);
      im.onerror = () => reject(new Error(`Cannot load ${file}`));
      im.src = new URL(file, this.root).href;
    });
    this.remember(this.images, file, pending, 20);
    try { return await pending; } catch (e) { this.images.delete(file); throw e; }
  }
  async data(file) {
    if (this.pixels.has(file)) return this.pixels.get(file);
    const im = await this.image(file), c = document.createElement('canvas');
    c.width = im.naturalWidth; c.height = im.naturalHeight;
    const ctx = c.getContext('2d', {willReadFrequently: true});
    ctx.drawImage(im, 0, 0);
    const value = ctx.getImageData(0, 0, c.width, c.height);
    return this.remember(this.pixels, file, value, 20);
  }
  clear() { this.images.clear(); this.pixels.clear(); }
  styles(modelId) {
    const m = this.models.get(modelId); if (!m) throw new Error(`Unknown model ${modelId}`);
    const result = m.legacyStyles.map(x => ({...x}));
    if (m.camouflageEnabled) {
      const existing = new Set(result.map(x => x.texture));
      for (const t of this.catalog.textures) if (!existing.has(t.id)) {
        result.push({id: `${m.id}_${result.length + 1}`, label: t.label, kind: 'camouflage', texture: t.id});
      }
    }
    return result;
  }
  async renderItem(itemId, {region = null} = {}) {
    const modelId = itemId.slice(0, itemId.lastIndexOf('_'));
    const style = this.styles(modelId).find(x => x.id === itemId);
    if (!style) throw new Error(`Unknown item ${itemId}`);
    return this.render(modelId, {...style, region});
  }
  async render(modelId, {kind = 'base', texture, hex, region = null} = {}) {
    const m = this.models.get(modelId); if (!m) throw new Error(`Unknown model ${modelId}`);
    if (!['base', 'solid', 'camouflage'].includes(kind)) throw new Error(`Unknown material ${kind}`);
    const base = await this.data(m.base);
    const c = document.createElement('canvas'); c.width = base.width; c.height = base.height;
    const ctx = c.getContext('2d'), out = new ImageData(new Uint8ClampedArray(base.data), base.width, base.height);
    if (kind !== 'base') {
      const mask = await this.data(m.mask);
      if (region && !m.regions[region]) throw new Error(`Unknown region ${region}`);
      const regionData = region ? await this.data(m.regions[region].file) : null;
      let pattern, colors;
      const parse = h => {
        if (!/^#[0-9a-f]{6}$/i.test(h)) throw new Error('Expected #RRGGBB');
        return [1, 3, 5].map(i => parseInt(h.slice(i, i + 2), 16));
      };
      if (kind === 'camouflage') {
        const t = this.textures.get(texture); if (!t) throw new Error(`Unknown camouflage ${texture}`);
        // Legacy preexisting painted models are allowed; new recipes restricted by catalog.
        if (!m.camouflageEnabled && !m.legacyStyles.some(s => s.texture === texture)) throw new Error('This model has no approved camouflage material');
        pattern = await this.data(this.catalog.patterns[t.pattern]);
        colors = this.palettes.get(t.palette).colors.map(parse);
      } else colors = [parse(hex)];
      for (let y = 0; y < base.height; y++) for (let x = 0; x < base.width; x++) {
        const i = (y * base.width + x) * 4;
        if (!base.data[i + 3]) continue;
        const mix = mask.data[i] / 255 * (regionData ? regionData.data[i] / 255 : 1);
        if (!mix) continue;
        const shade = Math.min(1.55, Math.max(.02, (base.data[i] + base.data[i + 1] + base.data[i + 2]) / (3 * m.shadeDivisor)));
        // Integer nearest sampling: the 512 map is exact for original 1024 texture.
        const index = pattern ? pattern.data[(Math.floor(y * pattern.height / base.height) * pattern.width + Math.floor(x * pattern.width / base.width)) * 4] : 0;
        const paint = colors[index];
        for (let k = 0; k < 3; k++) out.data[i + k] = Math.max(0, Math.min(255, Math.floor(base.data[i + k] * (1 - mix) + paint[k] * shade * mix)));
      }
    }
    ctx.putImageData(out, 0, 0); return c;
  }
}
