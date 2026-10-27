# Stage-A pandas wheel and offline dependency wheels are supplied from trusted Host.
FROM python:3.12-bookworm@sha256:5560e9ab8709f459489e5b8aa696eda8a07ef821e14bb122be62d91234bfa98b
COPY wheelhouse/ /opt/ccmvp/wheels/
# Exact dependency wheel SHA256 values reused from frozen
# research/mla/v04-mla-four-target-reentry-candidate.json; this artifact
# records metadata/offline-resolution only, NOT a runtime-import PASS.
RUN echo "e57b0784bf6fe3abd3f292284c124ffc1c6367e35e5b97cc298f63d53431ce08  /opt/ccmvp/wheels/pandas-0+untagged.1.g82c18c1-cp312-cp312-linux_x86_64.whl" | sha256sum -c - \
 && echo "fbde6962867ee75b48b0ee29b2b9372ec5d617799dbaf38e82dc0596f2f7738a  /opt/ccmvp/wheels/numpy-2.5.4-cp312-cp312-manylinux_2_27_x86_64.manylinux_2_28_x86_64.whl" | sha256sum -c - \
 && echo "a8b2bc7bffae282281c8140a97d3aa9c14da0b136dfe83f850eea9a5f7470427  /opt/ccmvp/wheels/python_dateutil-2.9.0.post0-py2.py3-none-any.whl" | sha256sum -c - \
 && echo "4721f391ed90541fddacab5acf947aa0d3dc7d27b2e1e8eda2be8970586c3274  /opt/ccmvp/wheels/six-1.17.0-py2.py3-none-any.whl" | sha256sum -c - \
 && python -m pip install --no-index --find-links=/opt/ccmvp/wheels \
 /opt/ccmvp/wheels/pandas-0+untagged.1.g82c18c1-cp312-cp312-linux_x86_64.whl \
 'numpy==2.5.4' 'python-dateutil==2.9.0.post0' 'six==1.17.0'
COPY pandas-job /opt/ccmvp/pandas-job
COPY orders.csv /opt/ccmvp/orders.csv
RUN chmod 0555 /opt/ccmvp/pandas-job && chmod 0444 /opt/ccmvp/orders.csv
