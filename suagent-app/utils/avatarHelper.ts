import CryptoJS from 'crypto-js';

/**
 * 生成头像背景渐变色
 * @param username 用户名
 * @returns 渐变色CSS类名
 */
export function generateAvatarGradient(username: string): string {
  // 生成用户名的MD5哈希
  const md5Hash = CryptoJS.MD5(username).toString();

  // 获取最后12位数字
  const last12Chars = md5Hash.slice(-12);

  // 将16进制字符串转换为数字
  const hexToNumber = (hex: string) => {
    const cleaned = hex.replace(/[^0-9a-fA-F]/g, '');
    return cleaned ? parseInt(cleaned, 16) : 0;
  };

  // 前6位作为第一个颜色，后6位作为第二个颜色
  const firstColorHex = last12Chars.slice(0, 6);
  const secondColorHex = last12Chars.slice(6, 12);

  const firstColorNum = hexToNumber(firstColorHex);
  const secondColorNum = hexToNumber(secondColorHex);

  // 将数字映射到0-360度的色相值
  const hue1 = firstColorNum % 360;
  const hue2 = secondColorNum % 360;

  // 使用HSL颜色模式，固定饱和度和亮度
  const color1 = `hsl(${hue1}, 70%, 50%)`;
  const color2 = `hsl(${hue2}, 70%, 50%)`;

  return `linear-gradient(135deg, ${color1}, ${color2})`;
}

/**
 * 获取头像显示文字
 * @param username 用户名
 * @returns 头像显示文字（第一个字符，大写）
 */
export function getAvatarText(username: string): string {
  if (!username) return '?';

  const firstChar = username.charAt(0);

  // 如果是小写字母，转换为大写
  if (/[a-z]/.test(firstChar)) {
    return firstChar.toUpperCase();
  }

  // 其他情况直接返回
  return firstChar;
}

/**
 * 生成智能体头像背景渐变色
 * @param agentId 智能体ID
 * @returns 渐变色CSS字符串
 */
export function generateAgentAvatarGradient(agentId: string): string {
  // 生成agent_id的MD5哈希
  const md5Hash = CryptoJS.MD5(agentId).toString();

  // 获取最后12位数字
  const last12Chars = md5Hash.slice(-12);

  // 将16进制字符串转换为数字
  const hexToNumber = (hex: string) => {
    const cleaned = hex.replace(/[^0-9a-fA-F]/g, '');
    return cleaned ? parseInt(cleaned, 16) : 0;
  };

  // 前6位作为第一个颜色，后6位作为第二个颜色
  const firstColorHex = last12Chars.slice(0, 6);
  const secondColorHex = last12Chars.slice(6, 12);

  const firstColorNum = hexToNumber(firstColorHex);
  const secondColorNum = hexToNumber(secondColorHex);

  // 将数字映射到0-360度的色相值
  const hue1 = firstColorNum % 360;
  const hue2 = secondColorNum % 360;

  // 使用HSL颜色模式，固定饱和度和亮度
  const color1 = `hsl(${hue1}, 70%, 50%)`;
  const color2 = `hsl(${hue2}, 70%, 50%)`;

  return `linear-gradient(135deg, ${color1}, ${color2})`;
}

/**
 * 获取智能体头像显示文字
 * @param agentName 智能体名称
 * @returns 头像显示文字（第一个字符，拉丁字母转大写）
 */
export function getAgentAvatarText(agentName: string): string {
  if (!agentName) return '?';

  const firstChar = agentName.charAt(0);

  // 如果是小写拉丁字母，转换为大写
  if (/[a-z]/.test(firstChar)) {
    return firstChar.toUpperCase();
  }

  // 其他情况直接返回（支持中文、大写字母、数字等）
  return firstChar;
}

/**
 * 获取头像完整的样式对象
 * @param username 用户名
 * @returns 包含背景色和文字的对象
 */
export function getAvatarStyles(username: string) {
  return {
    background: generateAvatarGradient(username),
    color: 'white',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontWeight: 'bold' as const,
    fontSize: '14px',
    width: '40px',
    height: '40px',
    borderRadius: '50%',
    textShadow: '0 1px 2px rgba(0,0,0,0.3)',
    border: '2px solid white',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
  };
}

/**
 * 获取智能体头像完整的样式对象
 * @param agentId 智能体ID
 * @param agentName 智能体名称
 * @param size 头像大小，默认64px
 * @returns 包含背景色和文字的对象
 */
export function getAgentAvatarStyles(agentId: string, agentName: string, size: number = 64) {
  return {
    background: generateAgentAvatarGradient(agentId),
    color: 'white',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontWeight: 'bold' as const,
    fontSize: `${size * 0.375}px`, // 相对于大小的字体大小
    width: `${size}px`,
    height: `${size}px`,
    borderRadius: '12px', // 智能体头像使用圆角矩形
    textShadow: '0 1px 2px rgba(0,0,0,0.3)',
    border: '2px solid white',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
  };
}