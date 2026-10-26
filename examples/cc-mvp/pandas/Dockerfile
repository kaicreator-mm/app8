# Stage-A pandas wheel and offline dependency wheels are supplied from trusted Host.
FROM python:3.12-bookworm@sha256:5560e9ab8709f459489e5b8aa696eda8a07ef821e14bb122be62d91234bfa98b
COPY wheelhouse/ /opt/ccmvp/wheels/
RUN echo "e57b0784bf6fe3abd3f292284c124ffc1c6367e35e5b97cc298f63d53431ce08  /opt/ccmvp/wheels/pandas-0+untagged.1.g82c18c1-cp312-cp312-linux_x86_64.whl" | sha256sum -c - \
 && python -m pip install --no-index --find-links=/opt/ccmvp/wheels \
 /opt/ccmvp/wheels/pandas-0+untagged.1.g82c18c1-cp312-cp312-linux_x86_64.whl \
 'numpy==2.5.4' 'python-dateutil==2.9.0.post0' 'six==1.17.0'
COPY pandas-job /opt/ccmvp/pandas-job
COPY orders.csv /opt/ccmvp/orders.csv
RUN chmod 0555 /opt/ccmvp/pandas-job && chmod 0444 /opt/ccmvp/orders.csv
