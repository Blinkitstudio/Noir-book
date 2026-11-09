#!/usr/bin/env bash
# Genera los efectos de sonido del kit con ffmpeg (sintetizados: sin problemas de licencia).
# Uso: bash generar_sfx.sh   → kit/sfx/*.wav
set -e
cd "$(dirname "$0")/sfx"
F="ffmpeg -v error -y"
# whoosh: ruido filtrado con barrido y envolvente (transiciones)
$F -f lavfi -i "anoisesrc=d=0.6:c=pink:a=0.8" -af "bandpass=f=1800:w=1.6,afade=t=in:d=0.25:curve=exp,afade=t=out:st=0.3:d=0.3,volume=1.6" -ar 48000 whoosh.wav
# whoosh largo para cambios de lugar
$F -f lavfi -i "anoisesrc=d=1.2:c=pink:a=0.8" -af "highpass=f=400,lowpass=f=5000,afade=t=in:d=0.7:curve=exp,afade=t=out:st=0.7:d=0.5,volume=1.4" -ar 48000 whoosh_largo.wav
# golpe grave (aparece un texto grande o un dato)
$F -f lavfi -i "aevalsrc='sin(2*PI*(55+90*exp(-t*18))*t)*exp(-t*7)':d=0.6:s=48000" -af "volume=1.8" golpe.wav
# pop corto (subtítulo de palabra clave, sticker)
$F -f lavfi -i "aevalsrc='sin(2*PI*(900-500*t*8)*t)*exp(-t*40)':d=0.15:s=48000" -af "volume=1.2" pop.wav
# click (interfaz, listas)
$F -f lavfi -i "anoisesrc=d=0.03:c=white:a=0.9" -af "highpass=f=2500,afade=t=out:d=0.03" -ar 48000 click.wav
# obturador de cámara (fotos)
$F -f lavfi -i "anoisesrc=d=0.18:c=white:a=0.9" -af "bandpass=f=3000:w=1.2,volume='if(lt(t,0.03),1,if(lt(t,0.09),0.15,if(lt(t,0.12),0.8,0)))':eval=frame,afade=t=out:st=0.12:d=0.06" -ar 48000 obturador.wav
# subida de tensión antes de un remate
$F -f lavfi -i "aevalsrc='0.5*sin(2*PI*(200+600*t*t)*t)*(t/1.5)':d=1.5:s=48000" -af "afade=t=out:st=1.4:d=0.1" riser.wav
# impacto con cola (stamp, cierre)
$F -f lavfi -i "anoisesrc=d=0.8:c=brown:a=1" -af "lowpass=f=900,afade=t=out:d=0.8:curve=exp,volume=2" -ar 48000 impacto.wav
ls -1 *.wav
