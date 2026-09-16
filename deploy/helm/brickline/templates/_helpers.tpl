{{- define "brickline.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "brickline.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{- define "brickline.labels" -}}
app.kubernetes.io/name: {{ include "brickline.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ printf "%s-%s" .Chart.Name .Chart.Version | quote }}
{{- end }}

{{- define "brickline.apiImage" -}}
{{- if .Values.api.image.digest -}}
{{ printf "%s@%s" .Values.api.image.repository .Values.api.image.digest }}
{{- else -}}
{{ printf "%s:%s" .Values.api.image.repository .Values.api.image.tag }}
{{- end -}}
{{- end }}

{{- define "brickline.webImage" -}}
{{- if .Values.web.image.digest -}}
{{ printf "%s@%s" .Values.web.image.repository .Values.web.image.digest }}
{{- else -}}
{{ printf "%s:%s" .Values.web.image.repository .Values.web.image.tag }}
{{- end -}}
{{- end }}
