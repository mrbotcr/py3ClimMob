import logging
import os
from subprocess import check_call

log = logging.getLogger(__name__)

__all__ = ["runRcreatePackages"]


def runRcreatePackages(user, project, sample, ncomparisons, combinations, request):
    path = os.path.join(request.registry.settings["user.repository"], *[user, project])
    if not os.path.exists(path):
        os.makedirs(path)
        rrepo = os.path.join(path, "r")
        os.makedirs(rrepo)
        rscript = os.path.join(
            request.registry.settings["r.scripts"], "randomization.R"
        )
        inputFile = os.path.join(rrepo, user + "_" + project + ".in")
        outputFile = os.path.join(rrepo, user + "_" + project + ".out")

        f = open(inputFile, "w+")
        f.write("%d\r\n" % (ncomparisons))
        f.write("%d\r\n" % (sample))
        f.write("%d\r\n" % (len(combinations)))
        for combination in combinations:
            f.write("%d\r\n" % (combination))
        f.close()

        args = []
        args.append("Rscript")
        args.append(rscript)
        args.append(inputFile)
        args.append(outputFile)
        # try:
        check_call(args)
        return outputFile
        # except CalledProcessError as e:
        #    msg = "Error dropping schema \n"
        #    msg = msg + "Error: \n"
        #    msg = msg + e.message + "\n"
        #    log.error(msg)
        #    return ""
